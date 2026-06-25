# Bull - Node.js Queue

## Setup

```javascript
const Queue = require('bull');
const redis = require('redis');

// Create queue
const emailQueue = new Queue('email', {
    redis: {
        host: 'localhost',
        port: 6379
    }
});

// Multiple queues
const taskQueue = new Queue('tasks');
const jobQueue = new Queue('jobs');
```

## Define Jobs

```javascript
// Add job processor
emailQueue.process(async (job) => {
    const { to, subject, body } = job.data;
    
    // Send email
    await sendEmail(to, subject, body);
    
    return { success: true, sent: to };
});

// With concurrency
emailQueue.process(5, async (job) => {
    // Process up to 5 jobs in parallel
    return await sendEmail(job.data);
});

// With progress reporting
taskQueue.process(async (job) => {
    for (let i = 0; i < 100; i++) {
        job.progress(i);
        await doWork();
    }
    return 'done';
});
```

## Add Jobs

```javascript
// Simple add
await emailQueue.add({
    to: 'user@example.com',
    subject: 'Hello',
    body: 'Message'
});

// With options
await emailQueue.add(
    { to, subject, body },
    {
        delay: 60000,           // Delay 60 seconds
        priority: 10,           // Higher = more priority
        attempts: 3,            // Retry 3 times
        backoff: {
            type: 'exponential',
            delay: 2000
        }
    }
);

// Repeat (cron)
await emailQueue.add(
    { action: 'daily-cleanup' },
    {
        repeat: {
            cron: '0 2 * * *'    // 2 AM daily
        }
    }
);
```

## Monitor Jobs

```javascript
// Get job
const job = await emailQueue.getJob(jobId);
console.log(job.progress());
console.log(job.state);        // 'waiting', 'active', 'completed', 'failed'

// Listen to events
emailQueue.on('completed', (job, result) => {
    console.log(`Job ${job.id} completed: ${result}`);
});

emailQueue.on('failed', (job, err) => {
    console.log(`Job ${job.id} failed: ${err}`);
});

emailQueue.on('progress', (job, progress) => {
    console.log(`Job ${job.id} progress: ${progress}%`);
});

// Count jobs
const waiting = await emailQueue.getWaitingCount();
const active = await emailQueue.getActiveCount();
const failed = await emailQueue.getFailedCount();
```

## Error Handling

```javascript
// Auto retry
emailQueue.process(async (job) => {
    try {
        return await sendEmail(job.data);
    } catch (err) {
        if (job.attemptsMade < job.opts.attempts) {
            throw err;  // Retry
        }
        // Max retries reached
        console.log(`Job ${job.id} failed permanently`);
        throw err;
    }
});

// Failed handler
emailQueue.on('failed', async (job, err) => {
    console.log(`Job ${job.id} failed: ${err.message}`);
    // Send alert, log to external service
});

// Stalled handler
emailQueue.on('stalled', (jobId) => {
    console.log(`Job ${jobId} stalled`);
});
```

## Advanced Patterns

### Job Chains

```javascript
// Chain jobs
const chainJob = await emailQueue.add({
    template: 'welcome',
    userId: 123
});

chainJob.addChild(
    taskQueue.add({ userId: 123 }),
    { queue: taskQueue }
);
```

### Job Flows

```javascript
// Parent-child jobs
const parent = await parentQueue.add({ data: 'parent' });

await childQueue.add(
    { parentId: parent.id },
    { parentKey: 'parent-flow' }
);

// Flow events
await parent.waitUntilFinished(eventEmitter);
```

### Bulk Operations

```javascript
// Add multiple jobs
const jobs = await Promise.all([
    emailQueue.add({ to: 'user1@example.com' }),
    emailQueue.add({ to: 'user2@example.com' }),
    emailQueue.add({ to: 'user3@example.com' })
]);
```

## Dashboard

```javascript
// Bull Board for monitoring
const { createBullBoard } = require('@bull-board/api');
const { BullAdapter } = require('@bull-board/api/bullAdapter');
const { ExpressAdapter } = require('@bull-board/express');

const serverAdapter = new ExpressAdapter();
createBullBoard({
    queues: [new BullAdapter(emailQueue), new BullAdapter(taskQueue)],
    serverAdapter: serverAdapter,
});

app.use('/admin/queues', serverAdapter.getRouter());
// Visit http://localhost:3000/admin/queues
```

## Best Practices

- ✅ Set appropriate retry strategies
- ✅ Use job priorities
- ✅ Monitor queue depth
- ✅ Set timeouts
- ✅ Use job names
- ✅ Report progress
- ✅ Handle failures gracefully
