/* address: 0x00490900 */
/* name: CUnitAI__Unk_00490900 */
/* signature: void __thiscall CUnitAI__Unk_00490900(void * this, void * param_1, void * param_2) */


void __thiscall CUnitAI__Unk_00490900(void *this,void *param_1,void *param_2)

{
  *(float *)this = *(float *)this - *(float *)param_1;
  *(float *)((int)this + 4) = *(float *)((int)this + 4) - *(float *)((int)param_1 + 4);
  *(float *)((int)this + 8) = *(float *)((int)this + 8) - *(float *)((int)param_1 + 8);
  return;
}
