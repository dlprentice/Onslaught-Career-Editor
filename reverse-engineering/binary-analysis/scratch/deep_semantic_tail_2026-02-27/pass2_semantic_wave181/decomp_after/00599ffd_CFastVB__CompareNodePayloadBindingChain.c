/* address: 0x00599ffd */
/* name: CFastVB__CompareNodePayloadBindingChain */
/* signature: int __thiscall CFastVB__CompareNodePayloadBindingChain(void * this, int param_1, int param_2, int param_3, int param_4) */


int __thiscall
CFastVB__CompareNodePayloadBindingChain(void *this,int param_1,int param_2,int param_3,int param_4)

{
  byte bVar1;
  int iVar2;
  bool bVar3;
  int iVar4;
  byte *pbVar5;
  undefined3 extraout_var;
  int extraout_EDX;
  byte *pbVar6;
  undefined1 local_20 [4];
  int local_1c;
  undefined1 local_14 [4];
  int local_10;
  void *local_8;

  if ((param_2 == 0) != (*(int *)(param_1 + 0x1c) == 0)) {
    return -1;
  }
  local_8 = this;
  if (param_2 != 0) {
    iVar4 = CDXTexture__LookupNamedFormatDescriptor
                      (*(void **)(*(int *)(param_1 + 0x1c) + 0x18),0,local_14);
    if ((iVar4 < 0) ||
       (iVar4 = CDXTexture__LookupNamedFormatDescriptor(*(void **)(param_2 + 0x18),0,local_20),
       iVar4 < 0)) {
      pbVar6 = *(byte **)(*(int *)(param_1 + 0x1c) + 0x18);
      pbVar5 = *(byte **)(param_2 + 0x18);
      do {
        bVar1 = *pbVar5;
        bVar3 = bVar1 < *pbVar6;
        if (bVar1 != *pbVar6) {
LAB_0059a08e:
          iVar4 = (1 - (uint)bVar3) - (uint)(bVar3 != 0);
          goto LAB_0059a093;
        }
        if (bVar1 == 0) break;
        bVar1 = pbVar5[1];
        bVar3 = bVar1 < pbVar6[1];
        if (bVar1 != pbVar6[1]) goto LAB_0059a08e;
        pbVar5 = pbVar5 + 2;
        pbVar6 = pbVar6 + 2;
      } while (bVar1 != 0);
      iVar4 = 0;
LAB_0059a093:
      if (iVar4 != 0) {
        return -1;
      }
    }
    else if (local_10 != local_1c) {
      return -1;
    }
  }
  iVar4 = *(int *)(param_1 + 0x24);
  do {
    if (iVar4 == 0) {
LAB_0059a0fb:
      if (param_3 != 0) {
        return -1;
      }
      return 0;
    }
    if (param_3 == 0) {
      if (iVar4 != 0) {
        return -1;
      }
      goto LAB_0059a0fb;
    }
    iVar4 = *(int *)(*(int *)(iVar4 + 8) + 0x18);
    iVar2 = *(int *)(*(int *)(param_3 + 8) + 0x18);
    if (*(int *)(iVar4 + 0x1c) != *(int *)(iVar2 + 0x1c)) {
      return -1;
    }
    bVar3 = CFastVB__AreNodeTreesStructurallyEqual(*(int *)(iVar4 + 0x20),*(int *)(iVar2 + 0x20));
    iVar4 = extraout_EDX;
    if (CONCAT31(extraout_var,bVar3) == 0) {
      return -1;
    }
    do {
      iVar4 = *(int *)(iVar4 + 0xc);
      if (iVar4 == 0) break;
    } while (*(int *)(*(int *)(iVar4 + 8) + 4) != 5);
    do {
      param_3 = *(int *)(param_3 + 0xc);
      if (param_3 == 0) break;
    } while (*(int *)(*(int *)(param_3 + 8) + 4) != 5);
  } while( true );
}
