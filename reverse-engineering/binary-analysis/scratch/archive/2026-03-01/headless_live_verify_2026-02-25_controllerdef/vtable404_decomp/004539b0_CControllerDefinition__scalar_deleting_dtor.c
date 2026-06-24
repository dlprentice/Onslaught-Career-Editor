/* address: 0x004539b0 */
/* name: CControllerDefinition__scalar_deleting_dtor */
/* signature: void * __thiscall CControllerDefinition__scalar_deleting_dtor(void * this, int flags) */


void * __thiscall CControllerDefinition__scalar_deleting_dtor(void *this,int flags)

{
  CControllerDefinition__dtor(this);
  if ((flags & 1U) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
