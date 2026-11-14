import { withLambda } from '@netlify/aws-lambda-compat';
import serverless from 'serverless-http';
import app from '../../server/index.mjs';
const handle = serverless(app);
export default withLambda((event, context) => handle(event, context));
export const config = { path: '/api/*', rateLimit: { action: 'rate_limit', aggregateBy: 'ip', windowSize: 60, windowLimit: 30 } };
