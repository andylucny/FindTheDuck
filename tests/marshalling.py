import sys
sys.path.append('../robot')
sys.path.append('../pc')

from marshaller import marshal
from demarshaller import demarshal

import numpy as np

image = np.random.rand(240,320,3).astype(np.uint8)
marshalled_image = marshal('img',image)
image2 = demarshal('img',marshalled_image)

assert np.min(image == image2)
