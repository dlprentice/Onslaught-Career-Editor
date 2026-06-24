/* address: 0x00453a90 */
/* name: CMenuItem__scalar_deleting_dtor */
/* signature: void * __thiscall CMenuItem__scalar_deleting_dtor(void * this, byte flags) */


void * __thiscall CMenuItem__scalar_deleting_dtor(void *this,byte flags)

{
  *(undefined ***)this = &PTR_CMenuItem__scalar_deleting_dtor_005db440;
  if ((flags & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
