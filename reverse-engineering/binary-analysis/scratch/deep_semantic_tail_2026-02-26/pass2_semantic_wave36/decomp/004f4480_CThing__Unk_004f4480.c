/* address: 0x004f4480 */
/* name: CThing__Unk_004f4480 */
/* signature: void __thiscall CThing__Unk_004f4480(void * this, int param_1, int param_2) */


void __thiscall CThing__Unk_004f4480(void *this,int param_1,int param_2)

{
  if ((*(int *)((int)this + 0x74) != 0) && ((*(uint *)(param_1 + 0x34) & 0x80000000) != 0)) {
    IScript__CreateThingRefWithSquad(param_1);
  }
  return;
}
