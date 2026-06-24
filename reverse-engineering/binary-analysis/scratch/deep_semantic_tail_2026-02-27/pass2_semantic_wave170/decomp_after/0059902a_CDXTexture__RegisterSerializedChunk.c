/* address: 0x0059902a */
/* name: CDXTexture__RegisterSerializedChunk */
/* signature: int CDXTexture__RegisterSerializedChunk(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CDXTexture__RegisterSerializedChunk(void)

{
  char cVar1;
  undefined4 uVar2;
  char *pcVar3;
  undefined4 *puVar4;
  undefined4 *ptr;
  int iVar5;
  char *extraout_EAX;
  int in_ECX;
  uint uVar6;
  char *pcVar7;
  char *pcVar8;
  bool bVar9;
  char *in_stack_00000004;
  char *in_stack_00000008;
  uint in_stack_0000000c;
  undefined4 *in_stack_00000010;

  if ((in_stack_00000008 != (char *)0x0) && (in_stack_00000004 == (char *)0x0)) {
    return -0x7fffbffb;
  }
  if (in_stack_00000008 == (char *)0xffffffff) {
    pcVar3 = in_stack_00000004;
    do {
      cVar1 = *pcVar3;
      pcVar3 = pcVar3 + 1;
    } while (cVar1 != '\0');
    in_stack_00000008 = pcVar3 + (1 - (int)(in_stack_00000004 + 1));
  }
  if ((in_stack_0000000c & 1) == 0) {
    in_stack_0000000c = in_stack_0000000c | 2;
  }
  if ((in_stack_0000000c & 2) != 0) {
    for (puVar4 = *(undefined4 **)(in_ECX + 8); puVar4 != (undefined4 *)0x0;
        puVar4 = (undefined4 *)puVar4[4]) {
      if (((*(byte *)(puVar4 + 2) & 2) != 0) && (in_stack_00000008 == (char *)puVar4[1])) {
        bVar9 = true;
        pcVar3 = in_stack_00000008;
        pcVar7 = in_stack_00000004;
        pcVar8 = (char *)*puVar4;
        do {
          if (pcVar3 == (char *)0x0) break;
          pcVar3 = pcVar3 + -1;
          bVar9 = *pcVar7 == *pcVar8;
          pcVar7 = pcVar7 + 1;
          pcVar8 = pcVar8 + 1;
        } while (bVar9);
        if (bVar9) {
          if (in_stack_00000010 != (undefined4 *)0x0) {
            *in_stack_00000010 = puVar4[3];
          }
          if (((in_stack_0000000c & 1) != 0) && ((in_stack_0000000c & 8) != 0)) {
            OID__FreeObject_Callback(in_stack_00000004);
          }
          return 0;
        }
      }
    }
  }
  CFastVB__Helper_00426fd0(0x14);
  if (ptr == (undefined4 *)0x0) {
LAB_005990af:
    iVar5 = -0x7ff8fff2;
  }
  else {
    if ((in_stack_0000000c & 1) == 0) {
      CFastVB__Helper_00426fd0((int)in_stack_00000008);
      *ptr = extraout_EAX;
      if (extraout_EAX == (char *)0x0) {
        OID__FreeObject_Callback(ptr);
        goto LAB_005990af;
      }
      pcVar3 = extraout_EAX;
      for (uVar6 = (uint)in_stack_00000008 >> 2; uVar6 != 0; uVar6 = uVar6 - 1) {
        *(undefined4 *)pcVar3 = *(undefined4 *)in_stack_00000004;
        in_stack_00000004 = in_stack_00000004 + 4;
        pcVar3 = pcVar3 + 4;
      }
      for (uVar6 = (uint)in_stack_00000008 & 3; uVar6 != 0; uVar6 = uVar6 - 1) {
        *pcVar3 = *in_stack_00000004;
        in_stack_00000004 = in_stack_00000004 + 1;
        pcVar3 = pcVar3 + 1;
      }
    }
    else {
      *ptr = in_stack_00000004;
    }
    if ((in_stack_0000000c & 4) == 0) {
      *(uint *)(in_ECX + 4) = *(int *)(in_ECX + 4) + 3U & 0xfffffffc;
    }
    uVar2 = *(undefined4 *)(in_ECX + 4);
    ptr[2] = in_stack_0000000c;
    ptr[4] = 0;
    ptr[3] = uVar2;
    ptr[1] = in_stack_00000008;
    *(int *)(in_ECX + 4) = (int)(in_stack_00000008 + *(int *)(in_ECX + 4));
    **(undefined4 **)(in_ECX + 0xc) = ptr;
    *(undefined4 **)(in_ECX + 0xc) = ptr + 4;
    if (in_stack_00000010 != (undefined4 *)0x0) {
      *in_stack_00000010 = ptr[3];
    }
    iVar5 = 0;
  }
  return iVar5;
}
