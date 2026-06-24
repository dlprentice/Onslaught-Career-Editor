/* address: 0x0058e4b5 */
/* name: CTexture__ValidateInstructionOperandsAndReserveConstantSlots */
/* signature: int __thiscall CTexture__ValidateInstructionOperandsAndReserveConstantSlots(void * this, void * param_1, uint param_2) */


int __thiscall
CTexture__ValidateInstructionOperandsAndReserveConstantSlots(void *this,void *param_1,uint param_2)

{
  int *piVar1;
  uint uVar2;
  int iVar3;
  void *pvVar4;
  int iVar5;
  undefined4 uVar6;
  int unaff_EBX;
  uint uVar7;
  int *piVar8;
  bool bVar9;
  bool bVar10;
  int iVar11;
  char *pcVar12;
  int *local_8;

  pvVar4 = param_1;
  *(int *)((int)param_1 + 0x58) = *(int *)((int)this + 0x5c) << 2;
  iVar11 = *(int *)((int)param_1 + 0x30);
  local_8 = (int *)0x1;
  bVar9 = false;
  if (iVar11 == 0x1f) {
    local_8 = (int *)0x2;
  }
  if (*(int *)((int)this + 0x78) != 0) {
    if ((((iVar11 == 0x1a) || (iVar11 == 0x19)) || (iVar11 == 0x1c)) || (iVar11 == 0x1e)) {
      pcVar12 = "call, callnz, label, and ret instructions are not allowed in assembly fragments";
      iVar11 = 0x7e9;
LAB_0058e52d:
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)param_1 + 0x10,iVar11,(int)pcVar12);
      return -0x7fffbffb;
    }
    if (((((iVar11 == 0x14) || (iVar11 == 0x15)) ||
         ((iVar11 == 0x16 || ((iVar11 == 0x17 || (iVar11 == 0x18)))))) &&
        (*(int *)((int)param_1 + 0x48) != 0)) &&
       (*(int *)(*(int *)((int)param_1 + 0x48) + 0x10) == 0)) {
      pcVar12 = "Matrices cannot be specified in temp registers with the fragment linker";
      iVar11 = 0x7ea;
      goto LAB_0058e52d;
    }
  }
  iVar11 = *(int *)((int)param_1 + 0x3c);
  piVar8 = local_8;
  if ((iVar11 != 0) && (*(int *)(iVar11 + 4) == 0x12)) {
    bVar9 = *(int *)(iVar11 + 0x10) == -1;
    if (*(int *)(iVar11 + 0x14) != 0) {
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)param_1 + 0x10,0x7de,0x5eccb8);
      *(undefined4 *)((int)this + 0x4c) = 1;
    }
    iVar11 = *(int *)(iVar11 + 0x28);
    piVar8 = (int *)((int)local_8 + 1);
    if (iVar11 != 0) {
      if ((*(int *)((int)this + 0x38) < 4) || (5 < *(int *)((int)this + 0x38))) {
        CTexture__AppendDiagnosticMessage(*(void **)this,(int)param_1 + 0x10,0x7d8,0x5ecc10);
        *(undefined4 *)((int)this + 0x4c) = 1;
      }
      else {
        bVar9 = *(int *)(iVar11 + 0x10) == -1 || bVar9;
        if (*(int *)(iVar11 + 0x28) != 0) {
          CTexture__AppendDiagnosticMessage(*(void **)this,(int)param_1 + 0x10,0x7d9,0x5ecc68);
          *(undefined4 *)((int)this + 0x4c) = 1;
        }
        piVar8 = (int *)((int)local_8 + 2);
      }
    }
  }
  local_8 = piVar8;
  if ((*(int *)((int)param_1 + 0x40) != 0) && (*(int *)(*(int *)((int)param_1 + 0x40) + 4) == 0x12))
  {
    iVar11 = *(int *)((int)this + 0x38);
    if (((-1 < iVar11) && (iVar11 < 2)) || ((5 < iVar11 && (iVar11 < 0xb)))) {
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)param_1 + 0x10,0x7e5,0x5ecbdc);
      *(undefined4 *)((int)this + 0x4c) = 1;
    }
    iVar11 = *(int *)((int)param_1 + 0x40);
    local_8 = (int *)((int)local_8 + 1);
    if (*(int *)(iVar11 + 0x10) == -1) {
      bVar9 = true;
    }
    if ((*(int *)(iVar11 + 0x14) != 0) && (*(int *)(iVar11 + 0x14) != 0xd000000)) {
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)param_1 + 0x10,0x7e3,0x5ecbac);
      *(undefined4 *)((int)this + 0x4c) = 1;
    }
    if (*(int *)(iVar11 + 0x28) != 0) {
      CTexture__AppendDiagnosticMessage(*(void **)this,(int)param_1 + 0x10,0x7e4,0x5ecb60);
      *(undefined4 *)((int)this + 0x4c) = 1;
    }
  }
  param_1 = (void *)0x0;
  piVar8 = (int *)((int)pvVar4 + 0x44);
  do {
    iVar11 = *piVar8;
    if (iVar11 == 0) break;
    iVar5 = *(int *)((int)pvVar4 + 0x30);
    piVar1 = (int *)((int)local_8 + 1);
    if (((iVar5 != 0x51) && (iVar5 != 0x30)) && (iVar5 != 0x2f)) {
      if (*(int *)(iVar11 + 0x10) == -1) {
        bVar9 = true;
      }
      iVar11 = *(int *)(iVar11 + 0x28);
      if (iVar11 != 0) {
        if (*(int *)(iVar11 + 0x10) == -1) {
          bVar9 = true;
        }
        if (*(int *)(iVar11 + 0x28) != 0) {
          CTexture__AppendDiagnosticMessage(*(void **)this,(int)pvVar4 + 0x10,0x7d9,0x5ecc68);
          *(undefined4 *)((int)this + 0x4c) = 1;
        }
        if (*(int *)((int)this + 0x38) != 0) {
          piVar1 = (int *)((int)local_8 + 2);
        }
      }
    }
    local_8 = piVar1;
    param_1 = (void *)((int)param_1 + 1);
    piVar8 = piVar8 + 1;
  } while (param_1 < (void *)0x4);
  iVar11 = CTexture__EnsurePendingConstantCapacity(this,(int)local_8,unaff_EBX);
  if (iVar11 < 0) {
    return iVar11;
  }
  iVar11 = *(int *)((int)this + 0x5c) + (int)local_8;
  uVar7 = *(uint *)((int)pvVar4 + 0x30);
  if ((uVar7 != 3) ||
     (((iVar5 = *(int *)((int)this + 0x38), iVar5 < 0 || (5 < iVar5)) &&
      ((iVar5 < 10 || (0xe < iVar5)))))) goto LAB_0058e85d;
  iVar5 = *(int *)((int)pvVar4 + 0x48);
  uVar2 = *(uint *)(iVar5 + 0x14);
  uVar6 = 0x7000000;
  uVar7 = 2;
  if (uVar2 < 0x7000001) {
    if (uVar2 == 0x7000000) {
      *(undefined4 *)(iVar5 + 0x14) = 0x8000000;
      goto LAB_0058e85d;
    }
    if (uVar2 == 0) {
      *(undefined4 *)(iVar5 + 0x14) = 0x1000000;
      goto LAB_0058e85d;
    }
    if (uVar2 == 0x1000000) {
      *(undefined4 *)(iVar5 + 0x14) = 0;
      goto LAB_0058e85d;
    }
    uVar6 = 0x2000000;
    if (uVar2 == 0x2000000) {
      *(undefined4 *)(iVar5 + 0x14) = 0x3000000;
      goto LAB_0058e85d;
    }
    if (uVar2 != 0x3000000) {
      uVar6 = 0x4000000;
      if (uVar2 == 0x4000000) {
        *(undefined4 *)(iVar5 + 0x14) = 0x5000000;
        goto LAB_0058e85d;
      }
      if (uVar2 != 0x5000000) {
        bVar10 = uVar2 == 0x6000000;
        goto LAB_0058e7cc;
      }
    }
  }
  else if (uVar2 != 0x8000000) {
    if ((uVar2 != 0x9000000) && (uVar2 != 0xa000000)) {
      uVar6 = 0xb000000;
      if (uVar2 == 0xb000000) {
        *(undefined4 *)(iVar5 + 0x14) = 0xc000000;
        goto LAB_0058e85d;
      }
      if (uVar2 == 0xc000000) goto LAB_0058e85a;
      bVar10 = uVar2 == 0xd000000;
LAB_0058e7cc:
      if (!bVar10) goto LAB_0058e85d;
    }
    CTexture__AppendDiagnosticMessage(*(void **)this,(int)pvVar4 + 0x10,0x7dd,0x5ecb2c);
    *(undefined4 *)((int)this + 0x4c) = 1;
    goto LAB_0058e85d;
  }
LAB_0058e85a:
  *(undefined4 *)(iVar5 + 0x14) = uVar6;
LAB_0058e85d:
  if (*(int *)((int)pvVar4 + 0x54) != 0) {
    uVar7 = uVar7 | 0x40000000;
  }
  if (*(int *)((int)pvVar4 + 0x40) != 0) {
    uVar7 = uVar7 | 0x10000000;
  }
  iVar5 = *(int *)((int)this + 0x38);
  if (((0 < iVar5) && (iVar5 < 6)) || ((9 < iVar5 && (iVar5 < 0xf)))) {
    uVar7 = uVar7 | ((int)local_8 + -1) * 0x1000000;
  }
  iVar5 = *(int *)((int)pvVar4 + 0x30);
  if (((iVar5 == 0x29) || (iVar5 == 0x2d)) || (iVar5 == 0x5e)) {
    uVar7 = uVar7 | (*(uint *)((int)pvVar4 + 0x38) & 7) << 0x10;
  }
  *(uint *)(*(int *)((int)this + 0x58) + *(int *)((int)this + 0x5c) * 4) = uVar7;
  *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
  iVar5 = *(int *)((int)this + 0x5c);
  if (*(int *)((int)pvVar4 + 0x30) == 0x1f) {
    *(uint *)(*(int *)((int)this + 0x58) + iVar5 * 4) = *(uint *)((int)pvVar4 + 0x38) | 0x80000000;
    *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
    iVar5 = *(int *)((int)this + 0x5c);
  }
  iVar3 = *(int *)((int)pvVar4 + 0x3c);
  if ((iVar3 != 0) && (*(int *)(iVar3 + 4) == 0x12)) {
    if ((*(int *)((int)this + 0x38) == 0) && (*(int *)(iVar3 + 0x20) == 0xf0000)) {
      iVar5 = *(int *)((int)pvVar4 + 0x30);
      if ((iVar5 == 0x15) || (iVar5 == 0x17)) {
        *(undefined4 *)(iVar3 + 0x20) = 0x70000;
      }
      else if (iVar5 == 0x18) {
        *(undefined4 *)(iVar3 + 0x20) = 0x30000;
      }
    }
    uVar7 = ((*(uint *)(iVar3 + 0x10) | 0xfffffff8) << 0x14 | *(uint *)(iVar3 + 0x10) & 0x18) << 8 |
            *(uint *)((int)pvVar4 + 0x34) & 0xff00000 | *(uint *)(iVar3 + 0x18) & 0x7ff |
            *(uint *)(iVar3 + 0x20) & 0xf0000;
    if (*(int *)(iVar3 + 0x28) != 0) {
      uVar7 = uVar7 | 0x2000;
    }
    *(uint *)(*(int *)((int)this + 0x58) + *(int *)((int)this + 0x5c) * 4) = uVar7;
    *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
    iVar3 = *(int *)(iVar3 + 0x28);
    iVar5 = *(int *)((int)this + 0x5c);
    if (iVar3 != 0) {
      *(uint *)(*(int *)((int)this + 0x58) + iVar5 * 4) =
           ((*(uint *)(iVar3 + 0x10) | 0xfffffff8) << 0x14 | *(uint *)(iVar3 + 0x10) & 0x18) << 8 |
           *(uint *)(iVar3 + 0x14) & 0xf000000 | *(uint *)(iVar3 + 0x18) & 0x7ff |
           *(uint *)(iVar3 + 0x24) & 0xff0000;
      *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
      iVar5 = *(int *)((int)this + 0x5c);
    }
  }
  iVar3 = *(int *)((int)pvVar4 + 0x40);
  if ((iVar3 != 0) && (*(int *)(iVar3 + 4) == 0x12)) {
    *(uint *)(*(int *)((int)this + 0x58) + iVar5 * 4) =
         ((*(uint *)(iVar3 + 0x10) | 0xfffffff8) << 0x14 | *(uint *)(iVar3 + 0x10) & 0x18) << 8 |
         *(uint *)(iVar3 + 0x14) & 0xf000000 | *(uint *)(iVar3 + 0x18) & 0x7ff |
         *(uint *)(iVar3 + 0x24) & 0xff0000;
    *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
    iVar5 = *(int *)((int)this + 0x5c);
  }
  iVar3 = *(int *)((int)pvVar4 + 0x30);
  if (iVar3 == 0x51) {
    param_1 = (void *)0x0;
    piVar8 = (int *)((int)pvVar4 + 0x44);
    do {
      iVar3 = *piVar8;
      if (iVar3 == 0) break;
      if ((4 < *(int *)(iVar3 + 0x10)) && (*(int *)(iVar3 + 0x10) < 9)) {
        *(float *)(*(int *)((int)this + 0x58) + iVar5 * 4) = (float)*(double *)(iVar3 + 0x18);
      }
      *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
      param_1 = (void *)((int)param_1 + 1);
      iVar5 = *(int *)((int)this + 0x5c);
      piVar8 = piVar8 + 1;
    } while (param_1 < (void *)0x4);
  }
  else if (iVar3 == 0x30) {
    param_1 = (void *)0x0;
    piVar8 = (int *)((int)pvVar4 + 0x44);
    do {
      iVar3 = *piVar8;
      if (iVar3 == 0) break;
      if ((*(int *)(iVar3 + 0x10) == 2) || (*(int *)(iVar3 + 0x10) == 4)) {
        *(undefined4 *)(*(int *)((int)this + 0x58) + iVar5 * 4) = *(undefined4 *)(iVar3 + 0x18);
      }
      *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
      param_1 = (void *)((int)param_1 + 1);
      iVar5 = *(int *)((int)this + 0x5c);
      piVar8 = piVar8 + 1;
    } while (param_1 < (void *)0x4);
  }
  else if (iVar3 == 0x2f) {
    *(uint *)(*(int *)((int)this + 0x58) + iVar5 * 4) =
         (uint)(*(int *)(*(int *)((int)pvVar4 + 0x44) + 0x18) != 0);
    *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
  }
  else {
    param_1 = (void *)0x0;
    local_8 = (int *)((int)pvVar4 + 0x44);
    do {
      iVar5 = *local_8;
      if (iVar5 == 0) break;
      if (((*(int *)((int)this + 0x38) == 0) && (*(int *)(iVar5 + 0x24) == 0xe40000)) &&
         ((iVar3 = *(int *)((int)pvVar4 + 0x30), iVar3 == 6 ||
          ((((iVar3 == 7 || (iVar3 == 0xe)) || (iVar3 == 0x4e)) ||
           ((iVar3 == 0xf || (iVar3 == 0x4f)))))))) {
        *(undefined4 *)(iVar5 + 0x24) = 0xff0000;
      }
      uVar7 = ((*(uint *)(iVar5 + 0x10) | 0xfffffff8) << 0x14 | *(uint *)(iVar5 + 0x10) & 0x18) << 8
              | *(uint *)(iVar5 + 0x14) & 0xf000000 | *(uint *)(iVar5 + 0x18) & 0x7ff |
              *(uint *)(iVar5 + 0x24) & 0xff0000;
      if (*(int *)(iVar5 + 0x28) != 0) {
        uVar7 = uVar7 | 0x2000;
      }
      *(uint *)(*(int *)((int)this + 0x58) + *(int *)((int)this + 0x5c) * 4) = uVar7;
      *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
      iVar5 = *(int *)(iVar5 + 0x28);
      if (iVar5 != 0) {
        if (*(int *)((int)this + 0x38) == 0) {
          if (((*(int *)(iVar5 + 0x10) != 3) || (*(int *)(iVar5 + 0x14) != 0)) ||
             ((*(int *)(iVar5 + 0x18) != 0 || (*(int *)(iVar5 + 0x24) != 0)))) {
            CTexture__AppendDiagnosticMessage(*(void **)this,(int)pvVar4 + 0x10,0x7d7,0x5ecaec);
            *(undefined4 *)((int)this + 0x4c) = 1;
          }
        }
        else {
          *(uint *)(*(int *)((int)this + 0x58) + *(int *)((int)this + 0x5c) * 4) =
               ((*(uint *)(iVar5 + 0x10) | 0xfffffff8) << 0x14 | *(uint *)(iVar5 + 0x10) & 0x18) <<
               8 | *(uint *)(iVar5 + 0x14) & 0xf000000 | *(uint *)(iVar5 + 0x18) & 0x7ff |
               *(uint *)(iVar5 + 0x24) & 0xff0000;
          *(int *)((int)this + 0x5c) = *(int *)((int)this + 0x5c) + 1;
        }
      }
      param_1 = (void *)((int)param_1 + 1);
      local_8 = local_8 + 1;
    } while (param_1 < (void *)0x4);
  }
  if (*(int *)((int)this + 0x5c) != iVar11) {
    CTexture__AppendDiagnosticMessage(*(void **)this,(int)pvVar4 + 0x10,0,0x5ecac0);
    *(undefined4 *)((int)this + 0x4c) = 1;
  }
  if (bVar9) {
    *(undefined4 *)((int)this + 100) = *(undefined4 *)((int)this + 0x5c);
  }
  else {
    iVar11 = CTexture__FlushPendingConstantTableWrites(this,(int)pvVar4 + 0x10,unaff_EBX);
    if (iVar11 < 0) {
      *(undefined4 *)((int)this + 0x50) = 1;
    }
  }
  return 0;
}
