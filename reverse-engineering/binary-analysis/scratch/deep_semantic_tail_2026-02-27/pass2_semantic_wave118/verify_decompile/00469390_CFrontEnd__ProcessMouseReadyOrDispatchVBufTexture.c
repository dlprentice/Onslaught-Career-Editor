/* address: 0x00469390 */
/* name: CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture */
/* signature: int __cdecl CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture(void * param_1, void * param_2, void * param_3, void * param_4, void * param_5) */


int __cdecl
CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture
          (void *param_1,void *param_2,void *param_3,void *param_4,void *param_5)

{
  uint uVar1;

  uVar1 = CFrontEnd__IsMouseInputReady(0x675688);
  if (uVar1 != 0) {
    return uVar1 & 0xffffff00;
  }
  uVar1 = CVBufTexture__Unk_00523bc0
                    ((float)param_1,(float)param_2,(float)param_3,(float)param_4,(int)param_5);
  return uVar1;
}
