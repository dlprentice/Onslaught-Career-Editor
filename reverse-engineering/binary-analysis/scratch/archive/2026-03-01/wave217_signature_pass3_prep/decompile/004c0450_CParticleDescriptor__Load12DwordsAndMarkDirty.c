/* address: 0x004c0450 */
/* name: CParticleDescriptor__Load12DwordsAndMarkDirty */
/* signature: void __thiscall CParticleDescriptor__Load12DwordsAndMarkDirty(void * this, void * src_block, void * context) */


void __thiscall
CParticleDescriptor__Load12DwordsAndMarkDirty(void *this,void *src_block,void *context)

{
  int iVar1;
  int iVar2;
  undefined4 *puVar3;

  iVar1 = *(int *)((int)this + 4);
  if (iVar1 != 0) {
    puVar3 = (undefined4 *)(iVar1 + 0x10);
    for (iVar2 = 0xc; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar3 = *(undefined4 *)src_block;
      src_block = (undefined4 *)((int)src_block + 4);
      puVar3 = puVar3 + 1;
    }
    *(undefined4 *)(iVar1 + 0xa0) = 1;
  }
  return;
}
