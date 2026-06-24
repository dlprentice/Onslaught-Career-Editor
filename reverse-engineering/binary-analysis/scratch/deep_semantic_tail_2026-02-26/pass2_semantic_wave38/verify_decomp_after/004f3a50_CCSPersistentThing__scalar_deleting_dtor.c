/* address: 0x004f3a50 */
/* name: CCSPersistentThing__scalar_deleting_dtor */
/* signature: void * __thiscall CCSPersistentThing__scalar_deleting_dtor(void * this, void * param_1, int param_2) */


void * __thiscall CCSPersistentThing__scalar_deleting_dtor(void *this,void *param_1,int param_2)

{
  CCSPersistentThing__dtor((int)this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
