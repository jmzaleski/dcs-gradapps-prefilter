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
        for key in self.key_list:
            assert len(self.menu_lines_dict[key])
        
    # print a cheesy little menu. If there is just one element in menu_lines_dict, then return 0
    # invalid or interrupt return -1
    # TODO: be nice to allow user to choose first char of line too.
    def menu(self):
        print(self.key_list)
        print(self.menu_lines_dict)
        if len(self.menu_lines_dict) == 1:
            return 0
        for key in self.key_list :
            print("%s %s" % (key, self.menu_lines_dict[key]))
        try:
            str_selection = input(self.prompt)  # this one for console.
            print (">>" + str_selection + "<<")
            if len(str_selection) == 0:
                #print("len zero, returning first key")
                return self.key_list[0] #just enter selects zero'th menu item
            else:
                if str_selection in self.key_list:
                    return str_selection
                else:
                    return None
        except KeyboardInterrupt:
            #here if user types control-C (or whatever terminal key interrupts)
            return -1
        except EOFError:
            return -1
        except:
            print("interrupt.. prob invalid selection:", str_selection)
            return -1


    
