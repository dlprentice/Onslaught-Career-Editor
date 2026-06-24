/* address: 0x0043aea0 */
/* name: CExplosionBasedOn__ReallocateObjectSlot */
/* signature: void __thiscall CExplosionBasedOn__ReallocateObjectSlot(void * this, int param_1, void * param_2) */


void __thiscall CExplosionBasedOn__ReallocateObjectSlot(void *this,int param_1,void *param_2)

{
  char cVar1;
  char *pcVar2;
  uint uVar3;
  uint uVar4;
  char *pcVar5;

  if (param_1 != 0) {
    OID__FreeObject(*(void **)((int)this + 0x28));
    uVar3 = 0xffffffff;
    pcVar2 = (char *)param_1;
    do {
      if (uVar3 == 0) break;
      uVar3 = uVar3 - 1;
      cVar1 = *pcVar2;
      pcVar2 = pcVar2 + 1;
    } while (cVar1 != '\0');
    pcVar2 = (char *)OID__AllocObject(~uVar3,4,s_C__dev_ONSLAUGHT2_WorldPhysicsMa_00625850,0x54a);
    uVar3 = 0xffffffff;
    *(char **)((int)this + 0x28) = pcVar2;
    do {
      pcVar5 = (char *)param_1;
      if (uVar3 == 0) break;
      uVar3 = uVar3 - 1;
      pcVar5 = (char *)(param_1 + 1);
      cVar1 = *(char *)param_1;
      param_1 = (int)pcVar5;
    } while (cVar1 != '\0');
    uVar3 = ~uVar3;
    pcVar5 = pcVar5 + -uVar3;
    for (uVar4 = uVar3 >> 2; uVar4 != 0; uVar4 = uVar4 - 1) {
      *(undefined4 *)pcVar2 = *(undefined4 *)pcVar5;
      pcVar5 = pcVar5 + 4;
      pcVar2 = pcVar2 + 4;
    }
    for (uVar3 = uVar3 & 3; uVar3 != 0; uVar3 = uVar3 - 1) {
      *pcVar2 = *pcVar5;
      pcVar5 = pcVar5 + 1;
      pcVar2 = pcVar2 + 1;
    }
  }
  return;
}
