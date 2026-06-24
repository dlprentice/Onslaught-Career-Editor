/* address: 0x004404f0 */
/* name: CThing__Helper_004404f0 */
/* signature: void __thiscall CThing__Helper_004404f0(void * this, void * param_1, void * param_2) */


void __thiscall CThing__Helper_004404f0(void *this,void *param_1,void *param_2)

{
  float fVar1;
  float fVar2;

  fVar1 = *(float *)((int)this + 8);
  fVar2 = *(float *)((int)this + 4);
  *(float *)param_1 = -*(float *)this;
  *(float *)((int)param_1 + 4) = -fVar2;
  *(float *)((int)param_1 + 8) = -fVar1;
  return;
}
