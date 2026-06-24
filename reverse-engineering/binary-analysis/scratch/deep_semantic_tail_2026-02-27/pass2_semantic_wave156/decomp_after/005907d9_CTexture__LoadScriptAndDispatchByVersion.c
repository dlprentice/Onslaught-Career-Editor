/* address: 0x005907d9 */
/* name: CTexture__LoadScriptAndDispatchByVersion */
/* signature: int __thiscall CTexture__LoadScriptAndDispatchByVersion(void * this, void * param_1, uint param_2, uint param_3, int param_4, void * param_5) */


int __thiscall
CTexture__LoadScriptAndDispatchByVersion
          (void *this,void *param_1,uint param_2,uint param_3,int param_4,void *param_5)

{
  uint uVar1;
  void *pvVar2;
  void *extraout_EAX;
  int iVar3;
  HMODULE hModule;
  FARPROC pFVar4;
  int *piVar5;
  void *unaff_EBX;
  char *pcVar6;
  undefined1 local_10 [4];
  undefined4 local_c;

  uVar1 = param_2;
  if ((param_2 & 0xfffffffa) != 0) {
    return -0x7789f794;
  }
  if (param_4 == 0) {
    return -0x7789f794;
  }
  *(undefined4 *)param_4 = 0;
  if (*(undefined4 **)((int)this + 0x34) != (undefined4 *)0x0) {
    (**(code **)**(undefined4 **)((int)this + 0x34))(1);
  }
  OID__FreeObject_Callback(*(void **)((int)this + 0x58));
  if (*(void **)((int)this + 0x78) != (void *)0x0) {
    CTexture__Dtor_ReleaseParserState_DeleteOnFlag
              (*(void **)((int)this + 0x78),(void *)0x1,(int)unaff_EBX);
  }
  DAT_009d2418 = this;
  *(undefined4 *)((int)this + 0x38) = 0xffffffff;
  *(void **)((int)this + 4) = param_1;
  *(int *)this = (int)param_1 + 4;
  *(undefined4 *)((int)this + 8) = 0;
  *(undefined4 *)((int)this + 0x30) = 0;
  *(undefined4 *)((int)this + 0x34) = 0;
  *(undefined4 *)((int)this + 0x58) = 0;
  *(undefined4 *)((int)this + 0x5c) = 0;
  *(undefined4 *)((int)this + 0x60) = 0;
  *(undefined4 *)((int)this + 100) = 0;
  *(undefined4 *)((int)this + 0x68) = 0;
  *(undefined4 *)((int)this + 0x4c) = 0;
  *(undefined4 *)((int)this + 0x50) = 0;
  *(undefined4 *)((int)this + 0x54) = 0;
  *(uint *)((int)this + 0x3c) = uVar1;
  *(undefined4 *)((int)this + 0x6c) = 0;
  *(undefined4 *)((int)this + 0x70) = 0;
  *(undefined4 *)((int)this + 0x74) = 0;
  if (param_3 != 0) {
    *(uint *)((int)this + 0x3c) = uVar1 | 4;
    *(uint *)((int)this + 0x7c) = param_3;
    CFastVB__Helper_00426fd0(100);
    if (extraout_EAX == (void *)0x0) {
      iVar3 = 0;
    }
    else {
      iVar3 = CTexture__Helper_0058f305(extraout_EAX);
    }
    *(int *)((int)this + 0x78) = iVar3;
    if (iVar3 == 0) {
      return -0x7ff8fff2;
    }
  }
  CTexture__Helper_00589846(*(void **)((int)this + 4),(int)&param_2,(void *)0x0,unaff_EBX);
  if (param_2 == 0) {
    CTexture__Helper_0058986b
              (*(void **)((int)this + 4),(int)this + 0x6c,(void *)((int)this + 0x70),unaff_EBX);
  }
  iVar3 = CTexture__Helper_00589802(*(void **)((int)this + 4),2,(int)unaff_EBX);
  if (iVar3 < 0) {
    return iVar3;
  }
  CTexture__Helper_0058f593(this);
  if ((*(int *)((int)this + 0x10) == 9) &&
     (iVar3 = CFastVB__Helper_00579b39(*(void **)((int)this + 0x18),1,local_10), -1 < iVar3)) {
    *(undefined4 *)((int)this + 0x10) = 0;
    *(undefined4 *)((int)this + 0x18) = local_c;
  }
  if (*(int *)((int)this + 0x10) != 0) {
    pcVar6 = "shader version expected";
    iVar3 = 0x7d1;
LAB_00590917:
    CTexture__Helper_0058c893(*(void **)this,(int)this + 0x10,iVar3,(int)pcVar6);
    goto LAB_00590925;
  }
  if (*(int *)((int)this + 0x18) == -0x1ff00) {
    CTexture__Helper_0058c95c(*(void **)this,(int)this + 0x10,0x7df);
    *(undefined4 *)((int)this + 0x18) = 0xfffe0101;
  }
  if (*(int *)((int)this + 0x18) == -0xff00) {
    CTexture__Helper_0058c95c(*(void **)this,(int)this + 0x10,0x7df);
    *(undefined4 *)((int)this + 0x18) = 0xffff0101;
  }
  uVar1 = *(uint *)((int)this + 0x18);
  if (uVar1 < 0xffff0103) {
    if (uVar1 == 0xffff0102) {
      *(undefined4 *)((int)this + 0x38) = 7;
    }
    else if (uVar1 == 0xfffe0101) {
      *(undefined4 *)((int)this + 0x38) = 0;
    }
    else if (uVar1 == 0xfffe0200) {
      *(undefined4 *)((int)this + 0x38) = 1;
    }
    else if (uVar1 == 0xfffe0201) {
      *(undefined4 *)((int)this + 0x38) = 2;
    }
    else if (uVar1 == 0xfffe02ff) {
      *(undefined4 *)((int)this + 0x38) = 3;
    }
    else if (uVar1 == 0xfffe0300) {
      *(undefined4 *)((int)this + 0x38) = 4;
    }
    else if (uVar1 == 0xfffe03ff) {
      *(undefined4 *)((int)this + 0x38) = 5;
    }
    else {
      if (uVar1 != 0xffff0101) goto LAB_00590a50;
      *(undefined4 *)((int)this + 0x38) = 6;
    }
  }
  else if (uVar1 == 0xffff0103) {
    *(undefined4 *)((int)this + 0x38) = 8;
  }
  else if (uVar1 == 0xffff0104) {
    *(undefined4 *)((int)this + 0x38) = 9;
  }
  else if (uVar1 == 0xffff0200) {
    *(undefined4 *)((int)this + 0x38) = 10;
  }
  else if (uVar1 == 0xffff0201) {
    *(undefined4 *)((int)this + 0x38) = 0xb;
  }
  else if (uVar1 == 0xffff02ff) {
    *(undefined4 *)((int)this + 0x38) = 0xc;
  }
  else if (uVar1 == 0xffff0300) {
    *(undefined4 *)((int)this + 0x38) = 0xd;
  }
  else {
    if (uVar1 != 0xffff03ff) {
LAB_00590a50:
      pcVar6 = "unrecognized shader version";
      iVar3 = 0x7d2;
      goto LAB_00590917;
    }
    *(undefined4 *)((int)this + 0x38) = 0xe;
  }
  if (*(int *)((int)this + 0x78) != 0) {
    if ((*(int *)((int)this + 0x38) < 0) || (3 < *(int *)((int)this + 0x38))) {
      CTexture__Helper_0058c893(*(void **)this,(int)this + 0x10,0x7d1,0x5ed2e0);
    }
    *(uint *)((int)this + 0x18) =
         (*(byte *)((int)this + 0x19) | 0x7ffe00) << 8 | *(uint *)((int)this + 0x18) & 0xff;
  }
  if (((*(byte *)((int)this + 0x3c) & 4) == 0) &&
     (((hModule = GetModuleHandleA("d3d9.dll"), hModule != (HMODULE)0x0 ||
       (hModule = LoadLibraryA("d3d9.dll"), hModule != (HMODULE)0x0)) &&
      (pFVar4 = GetProcAddress(hModule,"Direct3DShaderValidatorCreate9"), pFVar4 != (FARPROC)0x0))))
  {
    piVar5 = (int *)(*pFVar4)();
    *(int **)((int)this + 8) = piVar5;
    if ((piVar5 == (int *)0x0) ||
       (iVar3 = (**(code **)(*piVar5 + 0xc))(piVar5,CTexture__Helper_0058d821,this,0), -1 < iVar3))
    goto LAB_00590b2f;
  }
  else {
LAB_00590b2f:
    iVar3 = CTexture__Helper_0058e491(this,*(int *)((int)this + 0x18),(int)unaff_EBX);
    if ((-1 < iVar3) &&
       (iVar3 = CTexture__Helper_0058e3c3(this,(int)this + 0x10,(int)unaff_EBX), -1 < iVar3)) {
      if (*(int *)((int)this + 0x4c) == 0) {
        iVar3 = CTexture__ParseScriptWithYaccTables();
        if (iVar3 != 0) {
          *(undefined4 *)((int)this + 0x4c) = 1;
        }
        if (*(int *)((int)this + 0x4c) == 0) {
          if (*(int *)((int)this + 0x6c) != 0) {
            CTexture__Helper_0058986b(*(void **)((int)this + 4),(int)&param_1,(void *)0x0,unaff_EBX)
            ;
            pvVar2 = *(void **)((int)this + 0x6c);
            if ((pvVar2 < param_1) && (param_1 < (void *)(*(int *)((int)this + 0x70) + (int)pvVar2))
               ) {
              *(int *)((int)this + 0x70) = (int)param_1 - (int)pvVar2;
            }
          }
          if (((((*(int *)((int)this + 0x78) == 0) ||
                (iVar3 = CTexture__Helper_0058ecdb(this), -1 < iVar3)) &&
               (((*(byte *)((int)this + 0x3c) & 1) == 0 ||
                (iVar3 = CTexture__ParseDebugChunkAndRelocateBindings(this), -1 < iVar3)))) &&
              ((iVar3 = CTexture__Helper_0058e491(this,0xffff,(int)unaff_EBX), -1 < iVar3 &&
               (iVar3 = CTexture__Helper_0058e3c3(this,(int)this + 0x10,(int)unaff_EBX), -1 < iVar3)
               ))) && ((piVar5 = *(int **)((int)this + 8), piVar5 == (int *)0x0 ||
                       (iVar3 = (**(code **)(*piVar5 + 0x14))(piVar5), -1 < iVar3)))) {
            iVar3 = CTexture__Helper_0058c378(*(int *)this);
            if (iVar3 != 0) goto LAB_00590925;
            iVar3 = CTexture__Helper_0058f219(this,(void *)param_4,unaff_EBX);
            if (-1 < iVar3) {
              iVar3 = 0;
              goto LAB_00590c29;
            }
          }
          goto LAB_00590c1e;
        }
      }
LAB_00590925:
      iVar3 = -0x7789f4a7;
    }
  }
LAB_00590c1e:
  *(undefined4 *)((int)this + 0x4c) = 1;
LAB_00590c29:
  piVar5 = *(int **)((int)this + 8);
  if (piVar5 != (int *)0x0) {
    (**(code **)(*piVar5 + 8))(piVar5);
    *(undefined4 *)((int)this + 8) = 0;
  }
  CTexture__Helper_0058c08a(*(int *)((int)this + 4));
  return iVar3;
}
