import requests
import Configs


class GeneralTools(object):
    def url_add(self, url):
        res = requests.post(Configs.Configs.interface_host+':8886/url_add', data={'url': url})
        # res = requests.post(Configs.Confids.interface_host+':8886/url_add', data={'url': url})
        # return res
        return res

    def debug_decorate(is_debug):
        def inner_func(func):
            def inner_func2(*args, **kwargs):
                if is_debug:
                    func(*args, **kwargs)
            return inner_func2
        return inner_func

    @debug_decorate(True)
    def print_log(self, log):
        print(log)
