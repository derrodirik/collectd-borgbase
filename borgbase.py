import requests
import collectd


class BorgBaseService:

    def __init__(self):
        self.endpoint = "https://api.borgbase.com/graphql"
        self.api_key = None

        self.debug = False

    def dispatch(self, repo, value, data_type="bytes"):
        cld_dispatch = collectd.Values(
            plugin='borgbase',
            type=data_type,
            type_instance=repo
        )
        cld_dispatch.dispatch(values=[value])

        if self.debug:
            collectd.info('borgbase: Repo: ' + repo + ' Usage: ' + str(value))

    def config(self, config):
        api_key_set = False

        for node in config.children:
            key = node.key.lower()
            val = node.values[0]

            if key == 'apikey':
                self.api_key = val
                api_key_set = True
            elif key == 'debug':
                if val == "True":
                    self.debug = True
            else:
                collectd.info('borgbase: Unknown config key "%s"' % key)

        if not api_key_set:
            collectd.error('borgbase: API Key not set. Exiting')
            exit(1)

    def read(self):

        query = "query{repoList{id,name,currentUsage}}"
        header = {"Authorization": "Bearer " + self.api_key}

        total_usage = 0

        if self.debug:
            collectd.info('borgbase: Getting data from API')

        response = requests.post(self.endpoint,
                                 json={'query': query},
                                 headers=header)

        # Get JSON Object from request
        r = response.json()

        for repo in r['data']['repoList']:
            # Convert MB into bytes
            usage = int(repo['currentUsage'] * 1000000)

            # Calculate total Usage
            total_usage = total_usage + usage

            # Dispatch Usage of the Repo
            self.dispatch(repo=repo['name'], value=usage)

        # Dispatch Total Usage of all Repos
        self.dispatch(repo="total", value=total_usage)


bbs = BorgBaseService()

collectd.register_config(bbs.config)
collectd.register_read(bbs.read)
