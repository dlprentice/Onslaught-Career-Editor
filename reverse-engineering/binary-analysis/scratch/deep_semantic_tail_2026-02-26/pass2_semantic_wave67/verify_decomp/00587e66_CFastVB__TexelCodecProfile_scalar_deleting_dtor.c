/* address: 0x00587e66 */
/* name: CFastVB__TexelCodecProfile_scalar_deleting_dtor */
/* signature: void * __thiscall CFastVB__TexelCodecProfile_scalar_deleting_dtor(void * this, void * param_1, int param_2) */


void * __thiscall
CFastVB__TexelCodecProfile_scalar_deleting_dtor(void *this,void *param_1,int param_2)

{
  CFastVB__Helper_0058183d(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
