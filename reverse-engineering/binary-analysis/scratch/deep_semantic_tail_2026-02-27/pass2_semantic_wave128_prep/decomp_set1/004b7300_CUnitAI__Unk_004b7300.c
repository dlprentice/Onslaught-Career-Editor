/* address: 0x004b7300 */
/* name: CUnitAI__Unk_004b7300 */
/* signature: void * __thiscall CUnitAI__Unk_004b7300(void * this, void * param_1, int param_2) */


void * __thiscall CUnitAI__Unk_004b7300(void *this,void *param_1,int param_2)

{
  CMessageBox__ctor_like_004b7930(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
