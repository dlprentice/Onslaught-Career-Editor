/* address: 0x0048a4c0 */
/* name: CInfantryGuide__VFunc_01_0048a4c0 */
/* signature: void * __thiscall CInfantryGuide__VFunc_01_0048a4c0(void * this, void * param_1, int param_2) */


void * __thiscall CInfantryGuide__VFunc_01_0048a4c0(void *this,void *param_1,int param_2)

{
  CIBuffer__Unk_0048a4e0(this);
  if (((uint)param_1 & 1) != 0) {
    OID__FreeObject(this);
  }
  return this;
}
