/* address: 0x004fe540 */
/* name: CUnitAI__AccumulateForwardedCommandScore */
/* signature: void __thiscall CUnitAI__AccumulateForwardedCommandScore(void * this, void * param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CUnitAI__AccumulateForwardedCommandScore(void *this,void *param_1,float param_2)

{
  int iVar1;
  float local_8 [2];

  if (*(int *)((int)this + 0x218) == 0) {
    local_8[0] = -1.0;
    CEventManager__AddEvent_AtTime(&EVENT_MANAGER,0xfa5,this,local_8,0,(void *)0x0,(void *)0x0);
  }
  local_8[0] = (float)(longlong)ROUND((float)param_1 * _DAT_005db020);
  iVar1 = *(int *)((int)this + 0x218) + (int)local_8[0];
  *(int *)((int)this + 0x218) = iVar1;
  if (100 < iVar1) {
    *(undefined4 *)((int)this + 0x218) = 100;
  }
  *(undefined4 *)((int)this + 0x21c) = 10;
  return;
}
