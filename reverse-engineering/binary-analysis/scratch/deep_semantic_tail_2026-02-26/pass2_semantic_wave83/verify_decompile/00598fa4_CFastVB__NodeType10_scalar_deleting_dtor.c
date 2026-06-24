/* address: 0x00598fa4 */
/* name: CFastVB__NodeType10_scalar_deleting_dtor */
/* signature: void * __thiscall CFastVB__NodeType10_scalar_deleting_dtor(void * this, void * param_1, int param_2) */


void * __thiscall CFastVB__NodeType10_scalar_deleting_dtor(void *this,void *param_1,int param_2)

{
  CFastVB__NodeType10_dtor(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
