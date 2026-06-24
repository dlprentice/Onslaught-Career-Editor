/* address: 0x0050d680 */
/* name: CWorld__ReleaseSubObject_AndMaybeFree */
/* signature: void * __thiscall CWorld__ReleaseSubObject_AndMaybeFree(void * this, void * param_1, int param_2) */


void * __thiscall CWorld__ReleaseSubObject_AndMaybeFree(void *this,void *param_1,int param_2)

{
  CWorld__Helper_004bc2d0();
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
