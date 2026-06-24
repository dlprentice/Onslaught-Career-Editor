/* address: 0x0040c340 */
/* name: CEngine__Helper_0040c340 */
/* signature: void __thiscall CEngine__Helper_0040c340(void * this, void * param_1, int param_2) */


void __thiscall CEngine__Helper_0040c340(void *this,void *param_1,int param_2)

{
  float fVar1;
  float unaff_EDI;

  CGeneralVolume__Unk_00407940(this,*(int *)(*(int *)((int)param_1 + 0xa0) + 0x40),unaff_EDI);
  fVar1 = *(float *)(*(int *)((int)param_1 + 0xa0) + 0x40);
  *(float *)((int)this + 0x604) = fVar1 + fVar1 + *(float *)((int)this + 0x604);
  return;
}
