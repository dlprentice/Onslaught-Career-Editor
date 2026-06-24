/* address: 0x00598f60 */
/* name: CFastVB__Unk_00598f60 */
/* signature: int __thiscall CFastVB__Unk_00598f60(void * this, void * param_1, int param_2) */


int __thiscall CFastVB__Unk_00598f60(void *this,void *param_1,int param_2)

{
  *(undefined ***)this = &PTR_CFastVB__Unk_00598f60_005ef240;
  CFastVB__Helper_0059871c(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return (int)this;
}
