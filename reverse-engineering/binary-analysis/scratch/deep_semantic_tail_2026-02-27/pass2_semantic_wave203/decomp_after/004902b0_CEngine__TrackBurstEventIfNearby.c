/* address: 0x004902b0 */
/* name: CEngine__TrackBurstEventIfNearby */
/* signature: int CEngine__TrackBurstEventIfNearby(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CEngine__TrackBurstEventIfNearby(void)

{
  int iVar1;
  float fVar2;
  float *in_EAX;
  float *pfVar3;
  int in_ECX;
  float *pfVar4;
  undefined4 *puVar5;
  float *in_stack_00000004;
  float in_stack_0000000c;
  float in_stack_00000010;
  float local_14;
  undefined1 local_10 [16];

  if ((*(int *)(in_ECX + 0x1c0) < 0x10) &&
     (local_14 = 100.0, in_EAX = DAT_0089c9ac, 0 < (int)DAT_0089c9ac)) {
    puVar5 = &DAT_0089c9a4;
    pfVar4 = DAT_0089c9ac;
    do {
      pfVar3 = (float *)(*(code *)**(undefined4 **)*puVar5)(local_10);
      fVar2 = (pfVar3[1] - in_stack_00000004[1]) * (pfVar3[1] - in_stack_00000004[1]) +
              (*pfVar3 - *in_stack_00000004) * (*pfVar3 - *in_stack_00000004) +
              (pfVar3[2] - in_stack_00000004[2]) * (pfVar3[2] - in_stack_00000004[2]);
      if (fVar2 < local_14) {
        local_14 = fVar2;
      }
      puVar5 = puVar5 + 1;
      pfVar4 = (float *)((int)pfVar4 + -1);
    } while (pfVar4 != (float *)0x0);
    in_EAX = (float *)CONCAT22((short)((uint)pfVar3 >> 0x10),
                               (ushort)(local_14 < _DAT_005db020) << 8 |
                               (ushort)(NAN(local_14) || NAN(_DAT_005db020)) << 10 |
                               (ushort)(local_14 == _DAT_005db020) << 0xe);
    if (local_14 < _DAT_005db020) {
      local_14 = _DAT_005d8568 / local_14;
      iVar1 = *(int *)(in_ECX + 0x1c0);
      *(int *)(in_ECX + 0x1c0) = iVar1 + 1;
      in_EAX = (float *)(in_ECX + iVar1 * 0x1c);
      in_EAX[3] = *in_stack_00000004;
      in_EAX[4] = in_stack_00000004[1];
      in_EAX[5] = in_stack_00000004[2];
      in_EAX[6] = in_stack_00000004[3];
      in_EAX[1] = in_stack_0000000c;
      in_EAX[2] = local_14;
      *in_EAX = in_stack_00000010 * _DAT_005d85d4;
    }
  }
  return (int)in_EAX;
}
