/* address: 0x00535330 */
/* name: CVM__VFunc_01_00535330 */
/* signature: void * __thiscall CVM__VFunc_01_00535330(void * this, void * param_1, int param_2) */


void * __thiscall CVM__VFunc_01_00535330(void *this,void *param_1,int param_2)

{
  IScript__Unk_00535350(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
