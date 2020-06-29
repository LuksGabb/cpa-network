import uuid
from django.shortcuts import redirect
from django.http import HttpResponse
from tracker.tasks.click import click as click_task
from tracker.tasks.conversion import conversion
from tracker.dao import TrackerCache


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def replace_macro(url: str, context: dict) -> str:
    url = url.replace('{click_id}', context['click_id'])
    url = url.replace('{clickid}', context['click_id'])
    url = url.replace('{pid}', context['pid'])
    # url = url.replace('{ref_code}', str(context['ref_code']))
    return url


def click(request):
    offer_id = request.GET.get('offer_id')
    pid = request.GET.get('pid')
    if not offer_id or not pid:
        return HttpResponse("Missing parameters", status=400)

    offer_data = TrackerCache.get_offer(offer_id)
    if not offer_data:
        return HttpResponse(status=404)

    click_id = uuid.uuid4().hex

    data = {
        'click_id': click_id,
        'offer_id': offer_id,
        'pid': pid,
        'ip': get_client_ip(request),
        'ua': request.META['HTTP_USER_AGENT'],
        'sub1': request.GET.get('sub1', ""),
        'sub2': request.GET.get('sub2', ""),
        'sub3': request.GET.get('sub3', ""),
        'sub4': request.GET.get('sub4', ""),
        'sub5': request.GET.get('sub5', ""),
    }

    click_task.delay(data)

    context = {
        'click_id': click_id,
        'pid': pid,
    }
    url = replace_macro(offer_data['tracking_link'], context)

    return redirect(url)


def postback(request):
    click_id = request.GET.get('click_id')
    goal = request.GET.get('goal', '1')
    try:
        sum_ = float(request.GET.get('sum', ''))
    except ValueError:
        sum_ = 0.0

    if not click_id:
        resp = HttpResponse("Missing click_id")
        resp.status_code = 400
        return resp

    data = {
        'click_id': click_id,
        'goal': goal,
        'sum': sum_,
    }
    conversion.delay(data)

    return HttpResponse("Conversion logged")
