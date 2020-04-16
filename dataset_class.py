import os, sys, shutil, string, random
from pathlib import Path
import numpy as np

class dataset:
  def __init__(self, dtset_folder=None, dict_files=None):
  
    # the dataset can be created with the folder path or a dict_file
    assert dtset_folder!=None or dict_files!=None
  
    if dtset_folder != None:
      self.p = Path(dtset_folder)
      assert self.p.is_dir()
      
      self.name = self.p.name
      self.parent = self.p.parent
      
      self.classes = [x.name for x in list(self.p.glob('*')) if x.is_dir()]
      
      self.dict_nfiles = {}
      for class_ in self.classes:
        self.dict_nfiles[class_] = len(list((self.p/class_).glob('*png')))

      self.dict_files = {}
      for class_ in self.classes:
        self.dict_files[class_] = list((self.p/class_).glob('*png')) # jah eh o caminho completo

      self.dataset_type = 'real'
      
      self.dict_new_files = {}
      self.dict_new_nfiles = {}
      
      self.list_operations = []
      
    elif dict_files != None:
      
      # procurando a pasta-pai do dataset
      p = next(iter(dict_files.values()))[0]
      self.p = Path(*p.parts[:-2])
      
      self.name = self.p.name
      self.parent = self.p.parent
      
      # when the dataset come from a dict_file, its virtual because it is not written in the disk
      self.dataset_type = 'virtual'  
      self.dict_files = dict_files

      self.classes = list(dict_files.keys())

      self.dict_nfiles = {}
      for class_ in self.classes:
        self.dict_nfiles[class_] = len(dict_files[class_])

      self.dict_new_files = {}
      self.dict_new_nfiles = {}
      
      self.list_operations = []
     
    else:
      print ('Error. The class needs a folder path or a dict_file')
      sys.exit(0)
  
  @staticmethod
  def merge_datasets(dset1, dset2):
    dn = dataset.merge_dict_files(dset1.dict_files, dset2.dict_files)
    
    if isinstance(dn, dataset):
      return dn
    elif isinstance(dn, dict):
      return dataset(dict_files=dn)
    else:
      print ('Error, Wrong arg.')
      return None
    
    return dataset(dict_files=dn)
  
  @staticmethod
  def check_if_exists_name_in_dest(p1, parent2):
    if (parent2/p1.name).exists(): # if exists we have to change the name
      return check_if_exists_name(p1.parent/p1.with_name(str(p1.name)+'_1'), parent2)
    else:
      return p1

  @staticmethod
  def merge_dict_files(d1, d2, overwrite=False):
  
    dr = {}
        
    classes = list(set(list(d2.keys())).union(set(list(d2.keys()))))
  
    for class_ in classes:
      d1l = [pn for pn in d1[class_]]
      d2l = [pn for pn in d2[class_]]
      dr[class_] = d1l + d2l 

    return dr
  
  def __str__(self):
  
    s = '\n'
    s = s + 'Dataset {}'.format(self.name) + '\n'
    s = s + 'Path:' + str(self.p) + '\n'
    s = s + 'Dataset type: ' + str(self.dataset_type) + '\n'
  
    s = s + 'Found {} classes in dataset:'.format(len(self.classes)) + '\n'
    for class_ in self.classes:
      s = s + 'Class {}: {} files.'.format(class_, self.dict_nfiles[class_]) + '\n'

    if self.dict_new_nfiles and self.dict_new_files:
      s = s + 'New dict file to write:'
      for class_ in self.classes:
        s = s + 'Class {}: {} files.'.format(class_, self.dict_new_nfiles[class_]) + '\n'

    return s


  def write_to_disk(self, name, verbose=True):
    if self.dataset_type != 'virtual':
      print ('Error: For the dataset to be written it must be virtual.')
      return None
    else:
      if name == self.name:
        print ('Error: You have to change the new dataset name.')
        return None
      else:
        if (self.p.with_name(name)).exists():
          print ('File/folder {} exists. Try another.'.format(self.p.with_name(name)))
          return None
        else:
          # create the destination folders first        
          for class_ in self.classes:
            os.makedirs(self.p.with_name(name)/class_)
            
          # copy files
          for class_ in self.classes:
            for file_ in self.dict_files[class_]:
              # put a random tag to the file paths names to not overwrite nobody
              tag1 = ''
              for i in range(4):
                tag1 = tag1 + random.choice(string.ascii_letters)
              shutil.copyfile(file_, self.p.with_name(name)/class_/(file_.stem+'_'+tag1+'_'+file_.suffix))
          print ('Finished copy to folder {}'.format(self.p.with_name(name)))
          
          self.p = self.p.with_name(name)
          self.name = self.p.name
          self.parent = self.p.parent
          self.dataset_type = 'real'


  @staticmethod
  def undersample(d):
  
    if isinstance(d, dataset):
      dict_files = d.dict_files
    elif isinstance(d, dict):
      dict_files = d
    else:
      print ('Error, Wrong arg.')
      return None
  
    classes = list(dict_files.keys())
  
    # criar var local
    dict_nfiles = {}
    for class_ in classes:
      dict_nfiles[class_] = len(dict_files[class_])
  
    #
    list_nfiles = list()
    for class_ in classes:
      list_nfiles.append(dict_nfiles[class_])
      
    nfiles_under = min(list_nfiles)
    
    new_dict_files = {}
    for class_ in classes:
      new_dict_files[class_] = np.random.choice(dict_files[class_], size = nfiles_under)
      
    return dataset(dict_files=new_dict_files)
    
  @staticmethod
  def resample(q, d):
  
    if isinstance(d, dataset):
      dict_files = d.dict_files
    elif isinstance(d, dict):
      dict_files = d
    else:
      print ('Error, Wrong arg.')
      return None
 
    if isinstance(q, int):
      pass
    else:
      assert q<1
      assert q>0
    
    classes = list(dict_files.keys())
    
    # criar var local
    dict_nfiles = {}
    dict_new_nfiles = {}
    for class_ in classes:
      dict_nfiles[class_] = len(dict_files[class_])
      if isinstance(q, int):
        dict_new_nfiles[class_] = q  
      else:
        dict_new_nfiles[class_] = int(dict_nfiles[class_]*q)  
      
    
    new_dict_files = {}
    for class_ in classes:
      new_dict_files[class_] = np.random.choice(dict_files[class_], size = dict_new_nfiles[class_])
      
    return dataset(dict_files=new_dict_files)


#d = dataset(dtset_folder='Dataset/30_microm/macybloodsmear_resample_0.1')
#d2 = dataset.undersample(d.dict_files)
#print (d2)
#d2.write_to_disk('mc_test_us')
#print (d2)
#d3 = dataset('Dataset/30_microm/ACVP_4_resample_0.05')

#d4 = dataset.merge_datasets(d2, d3)
