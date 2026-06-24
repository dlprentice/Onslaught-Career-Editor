/* address: 0x005988f5 */
/* name: CFastVB__CompareNodeValuesByTagAndPayload */
/* signature: int __fastcall CFastVB__CompareNodeValuesByTagAndPayload(void * param_1) */


int __fastcall CFastVB__CompareNodeValuesByTagAndPayload(void *param_1)

{
  byte bVar1;
  int *in_EAX;
  byte *pbVar2;
  int iVar3;
  byte *pbVar4;
  bool bVar5;

  iVar3 = *(int *)param_1;
  if (iVar3 != *in_EAX) {
    return 0;
  }
  if (iVar3 < 9) {
    if (4 < iVar3) {
      if (*(double *)((int)param_1 + 8) != *(double *)(in_EAX + 2)) {
        return 0;
      }
      return 1;
    }
    if (iVar3 != 0) {
      if (iVar3 == 1) {
        pbVar4 = (byte *)(in_EAX + 2);
        pbVar2 = (byte *)((int)param_1 + 8);
        do {
          bVar1 = *pbVar2;
          bVar5 = bVar1 < *pbVar4;
          if (bVar1 != *pbVar4) goto LAB_005989b7;
          if (bVar1 == 0) break;
          bVar1 = pbVar2[1];
          bVar5 = bVar1 < pbVar4[1];
          if (bVar1 != pbVar4[1]) goto LAB_005989b7;
          pbVar2 = pbVar2 + 2;
          pbVar4 = pbVar4 + 2;
        } while (bVar1 != 0);
        goto LAB_0059894d;
      }
      if (iVar3 < 2) {
        return 1;
      }
      if (4 < iVar3) {
        return 1;
      }
    }
    bVar5 = *(int *)((int)param_1 + 8) == in_EAX[2];
    goto LAB_0059891f;
  }
  if (iVar3 == 9) {
    pbVar4 = (byte *)in_EAX[2];
    pbVar2 = *(byte **)((int)param_1 + 8);
    do {
      bVar1 = *pbVar2;
      bVar5 = bVar1 < *pbVar4;
      if (bVar1 != *pbVar4) goto LAB_005989b7;
      if (bVar1 == 0) break;
      bVar1 = pbVar2[1];
      bVar5 = bVar1 < pbVar4[1];
      if (bVar1 != pbVar4[1]) goto LAB_005989b7;
      pbVar2 = pbVar2 + 2;
      pbVar4 = pbVar4 + 2;
    } while (bVar1 != 0);
  }
  else {
    if (iVar3 != 10) {
      return 1;
    }
    pbVar4 = (byte *)in_EAX[2];
    pbVar2 = *(byte **)((int)param_1 + 8);
    do {
      bVar1 = *pbVar2;
      bVar5 = bVar1 < *pbVar4;
      if (bVar1 != *pbVar4) goto LAB_005989b7;
      if (bVar1 == 0) break;
      bVar1 = pbVar2[1];
      bVar5 = bVar1 < pbVar4[1];
      if (bVar1 != pbVar4[1]) goto LAB_005989b7;
      pbVar2 = pbVar2 + 2;
      pbVar4 = pbVar4 + 2;
    } while (bVar1 != 0);
  }
LAB_0059894d:
  iVar3 = 0;
LAB_005989bc:
  bVar5 = iVar3 == 0;
LAB_0059891f:
  if (!bVar5) {
    return 0;
  }
  return 1;
LAB_005989b7:
  iVar3 = (1 - (uint)bVar5) - (uint)(bVar5 != 0);
  goto LAB_005989bc;
}
