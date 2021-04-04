from datetime import datetime, timedelta
import requests
import collectd


class BorgBaseService:

    def __init__(self):
        self.endpoint = "https://api.borgbase.com/graphql"
        self.api_key = None

        self.next_request_time = None
        self.cached_response = None

    def dispatch(self, repo, value, data_type="bytes"):
        cld_dispatch = collectd.Values(
            plugin='borgbase',
            type=data_type,
            type_instance=repo
        )
        cld_dispatch.dispatch(values=[value])

        collectd.debug('borgbase: Repo: ' + repo + ' Usage: ' + str(value))

    def config(self, config):
        api_key_set = False

        for node in config.children:
            key = node.key.lower()
            val = node.values[0]

            if key == 'apikey':
                self.api_key = val
                api_key_set = True
            else:
                collectd.info('borgbase: Unknown config key "%s"' % key)

        if not api_key_set:
            collectd.error('borgbase: API Key not set. Exiting')
            raise ValueError

    def read(self):

        query = "query{repoList{id,name,currentUsage}}"
        header = {"Authorization": "Bearer " + self.api_key}

        collectd.debug('borgbase: Getting data from API')

        if self.cached_response is None or self.next_request_time < datetime.now():
            self.cached_response = requests.post(self.endpoint,
                                                 json={'query': query},
                                                 headers=header)
            self.next_request_time = datetime.now() + timedelta(minutes=15)
            collectd.debug('borgbase: Data requested. Next Request at: ' + self.next_request_time.strftime('%c'))

        else:
            collectd.debug('borgbase: Got Data from Cache.')

        # Get JSON Object from request
        r = self.cached_response.json()

        total_usage = 0

        for repo in r['data']['repoList']:
            # Convert MB into bytes
            usage = int(repo['currentUsage'] * 1000000)

            # Calculate total Usage
            total_usage += usage

            # Dispatch Usage of the Repo
            self.dispatch(repo=repo['name'], value=usage)

        # Dispatch Total Usage of all Repos
        self.dispatch(repo="total", value=total_usage)


bbs = BorgBaseService()

collectd.register_config(bbs.config)
collectd.register_read(bbs.read)
