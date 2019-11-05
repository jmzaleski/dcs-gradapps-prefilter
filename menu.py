'''
Created on Jul 14, 2016

@author: mzaleski
'''
class PrefilterMenu(object):
    '''
    print a cheesy little menu. returns -1 if interrupt or goofy key entered.
    '''

    def __init__(self, key_list, menu_lines_dict, prompt):
        '''
        Constructor
        '''
        self.menu_lines_dict = menu_lines_dict
        self.key_list = key_list
        self.prompt = prompt
        assert len(menu_lines_dict.keys()) == len(key_list)
        for key in key_list:
            assert len(menu_lines_dict[key])
        
    # print a cheesy little menu. If there is just one element in menu_lines_dict, then return 0
    # invalid or interrupt return -1
    # TODO: be nice to allow user to choose first char of line too.
    def menu(self):
        if len(self.menu_lines_dict) == 1:
            return 0
        n = 0    
        for a_matched_line in self.menu_lines_dict :
            print("%d %s" % (n, a_matched_line))
            n += 1
        try:
            str_selection = input(self.prompt)  # this one for console.
            #str_selection = input(self.prompt)     # pycharm debugger likes this better.
            #print (">>", str_selection, "<<")
            if len(str_selection) == 0:
                return 0 #just enter selects zero'th menu item
            else:
                #TODO check within bounds and return -1 if not?
                ix = int(str_selection)
                if ix < 0 or ix  >= len(self.menu_lines_dict):
                    return -1
                return ix
        except KeyboardInterrupt:
            #here if user types control-C (or whatever terminal key interrupts)
            return -1
        except EOFError:
            return -1
        except:
            print("interrupt.. prob invalid selection:", str_selection)
            return -1


    
