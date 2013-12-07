import django

is_before_1_6 = (django.VERSION[0] < 1) or (django.VERSION[0]
                                            == 1 and django.VERSION[1] < 6)
