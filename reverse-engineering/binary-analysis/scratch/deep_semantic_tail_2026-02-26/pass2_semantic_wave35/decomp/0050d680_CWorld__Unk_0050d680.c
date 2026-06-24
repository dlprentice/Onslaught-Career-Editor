/* address: 0x0050d680 */
/* name: CWorld__Unk_0050d680 */
/* signature: void * __thiscall CWorld__Unk_0050d680(void * this, void * param_1, int param_2) */


void * __thiscall CWorld__Unk_0050d680(void *this,void *param_1,int param_2)

{
  CWorld__Helper_004bc2d0();
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
