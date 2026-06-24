/* address: 0x00587e66 */
/* name: CFastVB__Unk_00587e66 */
/* signature: void * __thiscall CFastVB__Unk_00587e66(void * this, void * param_1, int param_2) */


void * __thiscall CFastVB__Unk_00587e66(void *this,void *param_1,int param_2)

{
  CFastVB__Helper_0058183d(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
