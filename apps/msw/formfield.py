import os

from django.forms import fields
from django.utils.translation import ugettext_lazy as _
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.core.files.uploadedfile import InMemoryUploadedFile

from PIL import Image

class ImageProcessField(fields.ImageField):
    print "in ImageProcessField"

    def to_python(self, data):
        # first get the image file
        # and also run ImageField's to_python
        f = super(ImageProcessField, self).to_python(data)
        print "((((((((((((((((((((("
        if f is None:
            return None

        # get the InMemoryUploadedFile from data
        """
        InMemoryUploadedFile(self, file, field_name, name, content_type, size, charset)
        *same* data.file = cStringIO.StringO object
        *same* data.field_name = u'image'
        data.name = u'assuny.gif'
        data.content_type = 'image/gif'
        data.size = 346
        data.charset = ""
        """

        # remember old name
        oldname = os.path.splitext(data.name)[0]

        # open into StringIO
        file = StringIO(data.read())
        image = Image.open(file)

        # resize Image
        image.thumbnail((100,100))

        # for saving non-jpgs: (from google)
        # Don't need it when saving as PNG
        #if image.mode not in ('L', 'RGB'):
        #    image = image.convert("RGB")
        
        # saving it into String IO       
        # http://stackoverflow.com/questions/646286/python-pil-how-to-write-png-image-to-string
        # into the JPEG format
        # http://www.pythonware.com/library/pil/handbook/image.htm
        new_file = StringIO()
        image.save(new_file, format="PNG")

        data.file = new_file
        data.name = oldname + '.png'
        data.content_type = 'image/png'
        #import pdb
        #pdb.set_trace()
        # FileField's to_python returns data
        return data
