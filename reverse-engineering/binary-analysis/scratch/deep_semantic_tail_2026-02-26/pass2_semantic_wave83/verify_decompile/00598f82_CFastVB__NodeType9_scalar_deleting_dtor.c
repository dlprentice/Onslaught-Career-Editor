/* address: 0x00598f82 */
/* name: CFastVB__NodeType9_scalar_deleting_dtor */
/* signature: int __thiscall CFastVB__NodeType9_scalar_deleting_dtor(void * this, void * param_1, int param_2) */


int __thiscall CFastVB__NodeType9_scalar_deleting_dtor(void *this,void *param_1,int param_2)

{
  *(undefined ***)this = &PTR_CFastVB__NodeType9_scalar_deleting_dtor_005ef250;
  CFastVB__Helper_0059871c(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return (int)this;
}
