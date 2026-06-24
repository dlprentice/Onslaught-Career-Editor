/* address: 0x00585bd3 */
/* name: CFastVB__TexelUnpackProfile_scalar_deleting_dtor */
/* signature: void * __thiscall CFastVB__TexelUnpackProfile_scalar_deleting_dtor(void * this, void * param_1, int param_2) */


void * __thiscall
CFastVB__TexelUnpackProfile_scalar_deleting_dtor(void *this,void *param_1,int param_2)

{
  CFastVB__Helper_00581263(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
