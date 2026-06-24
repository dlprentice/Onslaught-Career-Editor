/* address: 0x00591060 */
/* name: CDXTexture__Helper_00591060 */
/* signature: void CDXTexture__Helper_00591060(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void CDXTexture__Helper_00591060(void)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  uint uVar6;
  int *unaff_ESI;

  iVar1 = unaff_ESI[9];
  if (iVar1 == 1) {
    unaff_ESI[10] = 1;
    unaff_ESI[0xb] = 1;
    goto LAB_0059117d;
  }
  if (iVar1 != 3) {
    if (iVar1 == 4) {
      if ((unaff_ESI[0x4a] == 0) || (uVar6 = (uint)*(byte *)(unaff_ESI + 0x4b), uVar6 == 0)) {
        unaff_ESI[10] = 4;
        unaff_ESI[0xb] = 4;
      }
      else {
        if (uVar6 != 2) {
          iVar1 = *unaff_ESI;
          *(undefined4 *)(iVar1 + 0x14) = 0x72;
          *(uint *)(iVar1 + 0x18) = uVar6;
          (**(code **)(iVar1 + 4))();
        }
        unaff_ESI[10] = 5;
        unaff_ESI[0xb] = 4;
      }
    }
    else {
      unaff_ESI[10] = 0;
      unaff_ESI[0xb] = 0;
    }
    goto LAB_0059117d;
  }
  if (unaff_ESI[0x47] == 0) {
    if (unaff_ESI[0x4a] == 0) {
      piVar2 = (int *)unaff_ESI[0x37];
      iVar1 = *piVar2;
      iVar3 = piVar2[0x15];
      iVar4 = piVar2[0x2a];
      if (iVar1 == 1) {
        if ((iVar3 == 2) && (iVar4 == 3)) {
          unaff_ESI[10] = 3;
          unaff_ESI[0xb] = 2;
          goto LAB_0059117d;
        }
      }
      else if (((iVar1 == 0x52) && (iVar3 == 0x47)) && (iVar4 == 0x42)) goto LAB_00591103;
      iVar5 = *unaff_ESI;
      *(int *)(iVar5 + 0x18) = iVar1;
      *(int *)(iVar5 + 0x1c) = iVar3;
      *(int *)(iVar5 + 0x20) = iVar4;
      *(undefined4 *)(iVar5 + 0x14) = 0x6f;
    }
    else {
      uVar6 = (uint)*(byte *)(unaff_ESI + 0x4b);
      if (uVar6 == 0) {
LAB_00591103:
        unaff_ESI[10] = 2;
        unaff_ESI[0xb] = 2;
        goto LAB_0059117d;
      }
      if (uVar6 == 1) goto LAB_00591162;
      iVar5 = *unaff_ESI;
      *(undefined4 *)(iVar5 + 0x14) = 0x72;
      *(uint *)(iVar5 + 0x18) = uVar6;
    }
    (**(code **)(iVar5 + 4))();
  }
LAB_00591162:
  unaff_ESI[10] = 3;
  unaff_ESI[0xb] = 2;
LAB_0059117d:
  unaff_ESI[0xe] = 0;
  unaff_ESI[0x10] = 0;
  unaff_ESI[0x11] = 0;
  unaff_ESI[0x12] = 0;
  unaff_ESI[0x15] = 0;
  unaff_ESI[0x17] = 0;
  unaff_ESI[0x22] = 0;
  unaff_ESI[0x19] = 0;
  unaff_ESI[0x1a] = 0;
  unaff_ESI[0x1b] = 0;
  unaff_ESI[0xc] = 1;
  unaff_ESI[0xd] = 1;
  unaff_ESI[0xf] = 0x3ff00000;
  unaff_ESI[0x13] = 1;
  unaff_ESI[0x14] = 1;
  unaff_ESI[0x16] = 2;
  unaff_ESI[0x18] = 0x100;
  return;
}
