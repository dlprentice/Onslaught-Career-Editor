/* address: 0x004d30d0 */
/* name: CInfluenceMap__AccumulateThingFlags */
/* signature: void __thiscall CInfluenceMap__AccumulateThingFlags(void * this, int param_1, int param_2) */


void __thiscall CInfluenceMap__AccumulateThingFlags(void *this,int param_1,int param_2)

{
  if ((*(uint *)(param_1 + 0x34) & 0x400) != 0) {
    *(int *)((int)this + 8) = *(int *)((int)this + 8) + 1;
  }
  if ((*(uint *)(param_1 + 0x34) & 0x20000) != 0) {
    *(int *)((int)this + 0xc) = *(int *)((int)this + 0xc) + 1;
  }
  if ((*(uint *)(param_1 + 0x34) & 0x40000) != 0) {
    *(int *)((int)this + 0x10) = *(int *)((int)this + 0x10) + 1;
  }
  if ((*(uint *)(param_1 + 0x34) & 0x4000) != 0) {
    *(int *)((int)this + 0x14) = *(int *)((int)this + 0x14) + 1;
  }
  if ((*(uint *)(param_1 + 0x34) & 0x800) != 0) {
    *(int *)((int)this + 0x18) = *(int *)((int)this + 0x18) + 1;
  }
  return;
}
