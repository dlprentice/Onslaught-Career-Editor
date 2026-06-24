/* address: 0x00598fa4 */
/* name: CFastVB__Unk_00598fa4 */
/* signature: void * __thiscall CFastVB__Unk_00598fa4(void * this, void * param_1, int param_2) */


void * __thiscall CFastVB__Unk_00598fa4(void *this,void *param_1,int param_2)

{
  CFastVB__Unk_00598b81(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject_Callback(this);
  }
  return this;
}
