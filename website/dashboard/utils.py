from dashboard.models import Run


def update_bar(key, data):
    try:
        run = Run.objects.get(apikey=key)
    except Run.DoesNotExist:
        raise ValueError("Invalid API Key")

    bars = run.bar_set.all()
    for k, i in data.items():
        bar, new = bars.get_or_create(name=k, defaults={'maxval': 100, 'current': 0, 'run_id': run.id})
        if 'max' in i:
            bar.maxval = int(i['max'])
        if 'done' in i:
            bar.complete = bool(i['done'])
        if 'error' in i:
            bar.errored = bool(i['error'])
        if 'val' in i:
            bar.current = int(i['val'])
        bar.save()