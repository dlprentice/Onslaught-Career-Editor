/* address: 0x004b7ab0 */
/* name: CDropship__Unk_004b7ab0 */
/* signature: int __thiscall CDropship__Unk_004b7ab0(void * this, int param_1, void * param_2) */


int __thiscall CDropship__Unk_004b7ab0(void *this,int param_1,void *param_2)

{
  bool bVar1;
  short *psVar2;
  int iVar3;
  int *piVar4;
  int iVar5;
  int iVar6;

  bVar1 = false;
  iVar5 = 2;
  iVar6 = 0;
  piVar4 = (int *)((int)this + 0x16c);
  do {
    psVar2 = CText__GetStringById(&g_Text,*piVar4);
    iVar3 = CTexture__Unk_0055f2e8((void *)param_1,psVar2);
    if (iVar3 == 0) {
LAB_004b7b0f:
      bVar1 = true;
      iVar5 = iVar6;
    }
    else if ((!bVar1) && ((undefined1 *)*piVar4 == &LAB_00534dfa)) {
      psVar2 = CText__GetStringById(&g_Text,0xa336c2c);
      psVar2 = CDropship__Helper_0055f2a7((void *)param_1,psVar2);
      if (psVar2 != (short *)0x0) goto LAB_004b7b0f;
    }
    iVar6 = iVar6 + 1;
    piVar4 = piVar4 + 1;
    if (0xc < iVar6) {
      if (!bVar1) {
        FromWCHAR((short *)param_1);
        CConsole__Printf(&DAT_0066f580,s_ERROR__no_portraits_for___s__00630860);
      }
      iVar6 = 2;
      if (iVar5 != 3) {
        iVar6 = iVar5;
      }
      return iVar6;
    }
  } while( true );
}
