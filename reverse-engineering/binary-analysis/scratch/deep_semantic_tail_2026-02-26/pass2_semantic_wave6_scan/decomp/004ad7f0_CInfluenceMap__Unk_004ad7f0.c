/* address: 0x004ad7f0 */
/* name: CInfluenceMap__Unk_004ad7f0 */
/* signature: void __thiscall CInfluenceMap__Unk_004ad7f0(void * this, int param_1, int param_2) */


void __thiscall CInfluenceMap__Unk_004ad7f0(void *this,int param_1,int param_2)

{
  if (*(void **)((int)this + 0x24) != (void *)0x0) {
    OID__FreeObject(*(void **)((int)this + 0x24));
    *(undefined4 *)((int)this + 0x24) = 0;
    *(int *)((int)this + 0x14) = param_1;
    return;
  }
  *(undefined4 *)((int)this + 0x24) = 0;
  *(int *)((int)this + 0x14) = param_1;
  return;
}
