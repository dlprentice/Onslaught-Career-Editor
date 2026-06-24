/* address: 0x00520f70 */
/* name: CFEPVirtualKeyboard__MoveSelectionToRow */
/* signature: void __thiscall CFEPVirtualKeyboard__MoveSelectionToRow(void * this, int param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CFEPVirtualKeyboard__MoveSelectionToRow(void *this,int param_1,float param_2)

{
  short sVar1;
  uint uVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  int *piVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;

  iVar7 = param_1;
  do {
    iVar10 = *(int *)((int)this + 0x6ec);
    iVar8 = *(int *)((int)this + 0x6e8);
    iVar11 = 0;
    fVar5 = _DAT_005d856c;
    if (0 < iVar10) {
      piVar6 = (int *)((*(int *)((int)this + 0x6e4) + iVar8 + *(int *)((int)this + 0x6e4) * 4) *
                       0x70 + 0x58 + (int)this);
      iVar9 = iVar10;
      do {
        iVar11 = *piVar6;
        piVar6 = piVar6 + 2;
        iVar9 = iVar9 + -1;
        fVar5 = fVar5 + (float)iVar11;
        iVar11 = iVar10;
      } while (iVar9 != 0);
    }
    param_1 = 0;
    iVar10 = *(int *)((int)this + 0x6e4) * 5;
    iVar9 = iVar10 + iVar7;
    uVar2 = *(uint *)((int)this + (iVar11 + (iVar10 + iVar8) * 0xe) * 8 + 0x58);
    iVar10 = iVar9 * 0xe;
    *(int *)((int)this + 0x6e8) = iVar7;
    *(undefined4 *)((int)this + 0x6ec) = 0;
    fVar5 = (float)uVar2 * *(float *)((int)this + 0x6f4) + fVar5;
    sVar1 = *(short *)((int)this + iVar9 * 0x70 + 0x54);
    while (sVar1 != 0) {
      fVar3 = (float)*(uint *)((int)this + (iVar10 + *(int *)((int)this + 0x6ec)) * 8 + 0x58);
      fVar4 = fVar3 + (float)param_1;
      if (fVar5 <= fVar4) {
        *(float *)((int)this + 0x6f4) = (fVar5 - (float)param_1) / fVar3;
        goto LAB_00521087;
      }
      iVar7 = *(int *)((int)this + 0x6ec) + 1;
      *(int *)((int)this + 0x6ec) = iVar7;
      param_1 = (int)fVar4;
      sVar1 = *(short *)((int)this + (iVar7 + iVar10) * 8 + 0x54);
    }
    *(undefined4 *)((int)this + 0x6f4) = 0x3f000000;
    *(int *)((int)this + 0x6ec) = *(int *)((int)this + 0x6ec) + -1;
LAB_00521087:
    iVar7 = CFEPVirtualKeyboard__Helper_005214d0((int)this);
    if (iVar7 == 0) {
      return;
    }
    iVar8 = *(int *)((int)this + 0x6e8) - iVar8;
    if ((iVar8 != -1) && (iVar8 != 1)) {
      iVar8 = ((-2 < iVar8) - 1 & 2) - 1;
    }
    iVar7 = iVar8 + *(int *)((int)this + 0x6e8);
    if (iVar7 < 0) {
      iVar7 = 4;
    }
    else if (4 < iVar7) {
      iVar7 = 0;
    }
  } while( true );
}
