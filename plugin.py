import requests
from ruxit.api.base_plugin import RemoteBasePlugin
import logging
from base64 import b64encode


logger = logging.getLogger(__name__)

class PluginRemote(RemoteBasePlugin):
    def initialize(self, **kwargs):
        logger.info("Config: %s", self.config)
        self.url = self.config["url"]
        self.username = self.config["username"]
        self.password = self.config["password"]

    def query(self, **kwargs):
        #add username and password to the request
        request_url = self.url + "/PrismGateway/services/rest/v2.0/hosts/" 
        #request_url = self.url +"/api/nutanix/v3/vms/list"
        encoded_credentials = b64encode(bytes(f'{self.username}:{self.password}', encoding='ascii')).decode('ascii')
        auth_header = f'Basic {encoded_credentials}'
        #payload = '{"kind"= "vm"}'
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json','Authorization': f'{auth_header}', 'cache-control': 'no-cache'}
        r = requests.request('get', request_url, headers=headers, verify=False) #payload included here
        
        #Create topology
        topology = r.json()
        for line in topology['entities']:
            group_name = line['name']
            group = self.topology_builder.create_group(group_name, group_name)
            
            device = group.create_device(group_name, group_name)
            logger.info("Topology: group name=%s, device name=%s", group.name, device.name)
                #Collect stats
            stats = line['stats']
            device.absolute(key='avg_io_latency_usecs', value=stats['avg_io_latency_usecs'])
            device.absolute(key='content_cache_hit_ppm', value=float(stats['content_cache_hit_ppm'])/10000)
            device.absolute(key='content_cache_logical_memory_usage_bytes', value=stats['content_cache_logical_memory_usage_bytes'])
            device.absolute(key='content_cache_num_dedup_ref_count_pph', value=stats['content_cache_num_dedup_ref_count_pph'])
            device.absolute(key='content_cache_num_lookups', value=stats['content_cache_num_lookups'])
            device.absolute(key='content_cache_physical_memory_usage_bytes', value=stats['content_cache_physical_memory_usage_bytes'])
            device.absolute(key='controller_avg_io_latency_usecs', value=stats['controller_avg_io_latency_usecs'])
            device.absolute(key='hypervisor_cpu_usage_ppm', value=float(stats['hypervisor_cpu_usage_ppm'])/10000)
            device.absolute(key='hypervisor_memory_usage_ppm', value=float(stats['hypervisor_memory_usage_ppm'])/10000)
            device.absolute(key='controller_avg_write_io_latency_usecs', value=stats['controller_avg_write_io_latency_usecs'])