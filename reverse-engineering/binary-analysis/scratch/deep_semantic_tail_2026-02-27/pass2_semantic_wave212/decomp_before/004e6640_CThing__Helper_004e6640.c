/* address: 0x004e6640 */
/* name: CThing__Helper_004e6640 */
/* signature: void __thiscall CThing__Helper_004e6640(void * this, int param_1, int param_2, int param_3) */


void __thiscall CThing__Helper_004e6640(void *this,int param_1,int param_2,int param_3)

{
  if ((*(int *)((int)this + 0x74) != 0) && ((*(uint *)(param_2 + 0x34) & 0x80000000) != 0)) {
    IScript__CreateThingRefWithSquad(param_2);
  }
  return;
}
