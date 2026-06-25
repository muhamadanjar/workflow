# Job Scheduling & Cron

## APScheduler (Python)

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = BackgroundScheduler()

# Schedule job
@scheduler.scheduled_job('cron', hour=2, minute=0)
def cleanup_task():
    print("Daily cleanup at 2 AM")

# Manual schedule
scheduler.add_job(
    cleanup_task,
    'cron',
    hour=2,
    minute=0,
    id='daily_cleanup'
)

# Start scheduler
scheduler.start()
```

## Node-Cron (Node.js)

```javascript
const cron = require('node-cron');

// Run every day at 2 AM
cron.schedule('0 2 * * *', () => {
    console.log('Daily cleanup');
});

// Every 5 minutes
cron.schedule('*/5 * * * *', () => {
    console.log('Every 5 minutes');
});

// Custom validation
const task = cron.schedule('0 0 * * *', () => {
    console.log('Midnight');
});

task.stop();   // Stop
task.start();  // Resume
```

## Cron Expression Format

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of week (0 - 6) (Sunday to Saturday)
│ │ │ │ │
│ │ │ │ │
* * * * *
```

**Examples:**
```
0 2 * * *     - 2 AM daily
*/5 * * * *   - Every 5 minutes
0 0 * * 0     - Weekly (Sunday midnight)
0 0 1 * *     - Monthly (1st at midnight)
0 */6 * * *   - Every 6 hours
```

## Celery Beat

```python
# Periodic task definition
from celery import shared_task
from celery.schedules import crontab

app.conf.beat_schedule = {
    'cleanup-every-hour': {
        'task': 'myapp.tasks.cleanup',
        'schedule': crontab(minute=0),
    },
    'send-report-daily': {
        'task': 'myapp.tasks.send_report',
        'schedule': crontab(hour=8, minute=0),
    }
}

# Start beat scheduler
# celery -A myapp beat
```

## Bull Repeat Jobs

```javascript
// Repeat with cron
await queue.add(
    { action: 'daily-report' },
    {
        repeat: {
            cron: '0 8 * * *'  // 8 AM daily
        }
    }
);

// Fixed interval
await queue.add(
    { action: 'check-status' },
    {
        repeat: {
            every: 60000  // Every 60 seconds
        }
    }
);
```

## Best Practices

- ✅ Use UTC for all scheduled jobs
- ✅ Set job timeouts
- ✅ Log job execution
- ✅ Handle failed scheduled jobs
- ✅ Monitor scheduler health
