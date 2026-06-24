/* address: 0x004daba0 */
/* name: CEngine__FindNearbyHostileWithinProjectileRadius */
/* signature: int __fastcall CEngine__FindNearbyHostileWithinProjectileRadius(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CEngine__FindNearbyHostileWithinProjectileRadius(int param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  void *this;
  void *unaff_EDI;
  float local_10;
  float local_c;
  float local_8;

  iVar4 = CMapWho__GetFirstEntryWithinRadius
                    (*(float *)(param_1 + 0x1c),*(undefined4 *)(param_1 + 0x20),
                     *(undefined4 *)(param_1 + 0x24),*(undefined4 *)(param_1 + 0x28),
                     *(undefined4 *)(*(int *)(param_1 + 0xf0) + 0x90));
  do {
    if (iVar4 == 0) {
      return 0;
    }
    this = (void *)CMapWhoEntry__GetOwner();
    if ((((this != (void *)0x0) && (this != *(void **)(param_1 + 0xe8))) &&
        ((*(byte *)((int)this + 0x34) & 0x10) != 0)) && ((*(byte *)((int)this + 0x2c) & 4) == 0)) {
      CUnitAI__GetWorldPositionForTargeting(this,(int)&local_10,unaff_EDI);
      fVar1 = local_10 - *(float *)(param_1 + 0x1c);
      fVar2 = local_c - *(float *)(param_1 + 0x20);
      fVar3 = local_8 - *(float *)(param_1 + 0x24);
      fVar2 = fVar2 * fVar2 + fVar1 * fVar1 + fVar3 * fVar3;
      fVar1 = *(float *)(*(int *)(param_1 + 0xf0) + 0x90);
      if ((fVar2 < fVar1 * fVar1) && (_DAT_005d858c < fVar2)) {
        return (int)this;
      }
    }
    iVar4 = CMapWho__GetNextEntryWithinRadius();
  } while( true );
}
