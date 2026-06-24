/* address: 0x004be420 */
/* name: CEngine__Unk_004be420 */
/* signature: int CEngine__Unk_004be420(void) */


/* WARNING: Removing unreachable block (ram,0x004be946) */
/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CEngine__Unk_004be420(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;

  uVar4 = DAT_00809dbc;
  iVar1 = 1;
  *(undefined2 *)((int)&DAT_00809dc0 + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2) = 1;
  if ((DAT_00829dc0 == DAT_00809db4) && (uVar4 == DAT_00809db0)) {
    return 1;
  }
  iVar2 = DAT_00829dc0 - DAT_00809db4;
  if (iVar2 < 0) {
    iVar2 = -iVar2;
  }
  iVar3 = DAT_00809dbc - DAT_00809db0;
  if (iVar3 < 0) {
    iVar3 = -iVar3;
  }
  if (iVar3 < iVar2) {
    if (DAT_00809db4 < DAT_00829dc0) {
      iVar2 = iVar1;
      if (((0 < DAT_00829dc0) &&
          (iVar2 = 1, *(short *)(&DAT_00809bc0 + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2) == -1))
         && (uVar4 = CEngine__Unk_004be970(DAT_00809db8,DAT_00829dc0 + -1,DAT_00809dbc,1),
            iVar2 = iVar1, uVar4 != 0)) {
        iVar1 = 2;
        goto LAB_004be826;
      }
      if ((int)DAT_00809db0 < (int)DAT_00809dbc) {
        if (((0 < (int)DAT_00809dbc) &&
            (*(short *)((int)&DAT_00809dbc + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2 + 2) == -1))
           && (uVar4 = CEngine__Unk_004be970(DAT_00809db8,DAT_00829dc0,DAT_00809dbc - 1,iVar2),
              uVar4 != 0)) {
          iVar1 = 1;
          goto LAB_004be826;
        }
        if ((((int)DAT_00809dbc < 0xff) &&
            (*(short *)((int)&DAT_00809dc0 + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2 + 2) == -1))
           && (uVar4 = CEngine__Unk_004be970(DAT_00809db8,DAT_00829dc0,DAT_00809dbc + 1,iVar2),
              uVar4 != 0)) {
          iVar1 = 3;
          goto LAB_004be826;
        }
      }
      else {
        if ((((int)DAT_00809dbc < 0xff) &&
            (*(short *)((int)&DAT_00809dc0 + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2 + 2) == -1))
           && (uVar4 = CEngine__Unk_004be970(DAT_00809db8,DAT_00829dc0,DAT_00809dbc + 1,iVar2),
              uVar4 != 0)) {
          iVar1 = 3;
          goto LAB_004be826;
        }
        if (((0 < (int)DAT_00809dbc) &&
            (*(short *)((int)&DAT_00809dbc + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2 + 2) == -1))
           && (uVar4 = CEngine__Unk_004be970(DAT_00809db8,DAT_00829dc0,DAT_00809dbc - 1,iVar2),
              uVar4 != 0)) {
          iVar1 = 1;
          goto LAB_004be826;
        }
      }
      if (((DAT_00829dc0 < 0xff) &&
          (*(short *)((int)&DAT_00809fc0 + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2) == -1)) &&
         (uVar4 = CEngine__Unk_004be970(DAT_00809db8,DAT_00829dc0 + 1,DAT_00809dbc,iVar2),
         uVar4 != 0)) {
        iVar1 = 4;
        goto LAB_004be826;
      }
    }
    else {
      if (((DAT_00829dc0 < 0xff) &&
          (*(short *)((int)&DAT_00809fc0 + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2) == -1)) &&
         (uVar4 = CEngine__Unk_004be970(DAT_00809db8,DAT_00829dc0 + 1,DAT_00809dbc,1), uVar4 != 0))
      {
        iVar1 = 4;
        goto LAB_004be826;
      }
      if ((int)DAT_00809db0 < (int)DAT_00809dbc) {
        if (((0 < (int)DAT_00809dbc) &&
            (*(short *)((int)&DAT_00809dbc + (DAT_00829dc0 * 0x100 + DAT_00809dbc) * 2 + 2) == -1))
           && (uVar4 = CEngine__Unk_004be970(DAT_00809db8,DAT_00829dc0,DAT_00809dbc - 1,iVar1),
              uVar4 != 0)) {
          iVar1 = 1;
          goto LAB_004be826;
        }
        iVar1 = CEngine__Unk_004bead0();
        if (iVar1 != 0) {
          iVar1 = 3;
          goto LAB_004be826;
        }
      }
      else {
        iVar1 = CEngine__Unk_004bead0();
        if (iVar1 != 0) {
          iVar1 = 3;
          goto LAB_004be826;
        }
        iVar1 = CEngine__Unk_004bea10();
        if (iVar1 != 0) {
          iVar1 = 1;
          goto LAB_004be826;
        }
      }
      iVar1 = CEngine__Unk_004be9b0();
      if (iVar1 != 0) {
        iVar1 = 2;
        goto LAB_004be826;
      }
    }
  }
  else if ((int)DAT_00809db0 < (int)DAT_00809dbc) {
    iVar1 = CEngine__Unk_004bea10();
    if (iVar1 != 0) {
      iVar1 = 1;
      goto LAB_004be826;
    }
    if (DAT_00809db4 < DAT_00829dc0) {
      iVar1 = CEngine__Unk_004be9b0();
      if (iVar1 != 0) {
        iVar1 = 2;
        goto LAB_004be826;
      }
      iVar1 = CEngine__Unk_004bea70();
      if (iVar1 != 0) {
        iVar1 = 4;
        goto LAB_004be826;
      }
    }
    else {
      iVar1 = CEngine__Unk_004bea70();
      if (iVar1 != 0) {
        iVar1 = 4;
        goto LAB_004be826;
      }
      iVar1 = CEngine__Unk_004be9b0();
      if (iVar1 != 0) {
        iVar1 = 2;
        goto LAB_004be826;
      }
    }
    iVar1 = CEngine__Unk_004bead0();
    if (iVar1 != 0) {
      iVar1 = 3;
      goto LAB_004be826;
    }
  }
  else {
    iVar1 = CEngine__Unk_004bead0();
    if (iVar1 != 0) {
      iVar1 = 3;
      goto LAB_004be826;
    }
    if (DAT_00809db4 < DAT_00829dc0) {
      iVar1 = CEngine__Unk_004be9b0();
      if (iVar1 != 0) {
        iVar1 = 2;
        goto LAB_004be826;
      }
      iVar1 = CEngine__Unk_004bea70();
      if (iVar1 != 0) {
        iVar1 = 4;
        goto LAB_004be826;
      }
    }
    else {
      iVar1 = CEngine__Unk_004bea70();
      if (iVar1 != 0) {
        iVar1 = 4;
        goto LAB_004be826;
      }
      iVar1 = CEngine__Unk_004be9b0();
      if (iVar1 != 0) {
        iVar1 = 2;
        goto LAB_004be826;
      }
    }
    iVar1 = CEngine__Unk_004bea10();
    if (iVar1 != 0) {
      iVar1 = 1;
      goto LAB_004be826;
    }
  }
  iVar1 = 0;
LAB_004be826:
                    /* WARNING: Could not recover jumptable at 0x004be826. Too many branches */
                    /* WARNING: Treating indirect jump as call */
  iVar1 = (*(code *)(&PTR_LAB_004be94c)[iVar1])();
  return iVar1;
}
