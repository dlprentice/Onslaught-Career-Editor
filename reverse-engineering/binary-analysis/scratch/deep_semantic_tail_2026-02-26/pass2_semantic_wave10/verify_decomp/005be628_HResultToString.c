/* address: 0x005be628 */
/* name: HResultToString */
/* signature: int HResultToString(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int HResultToString(void)

{
  int in_stack_00000004;

  if (in_stack_00000004 < -0x7ff69ffe) {
    if (in_stack_00000004 == -0x7ff69fff) {
      return (int)"TRUST_E_SYSTEM_ERROR";
    }
    if (in_stack_00000004 < -0x7ff8f883) {
      if (in_stack_00000004 == -0x7ff8f884) {
switchD_005c6079_caseD_77c:
        return (int)"RPC_X_PIPE_CLOSED";
      }
      if (in_stack_00000004 < -0x7ff8ff7d) {
        if (in_stack_00000004 == -0x7ff8ff7e) {
switchD_005c4895_caseD_82:
          return (int)"ERROR_DIRECT_ACCESS_HANDLE";
        }
        if (in_stack_00000004 < -0x7ffbfe0e) {
          if (in_stack_00000004 == -0x7ffbfe0f) {
            return (int)"CO_E_ALREADYINITIALIZED";
          }
          if (in_stack_00000004 < -0x7ffd773a) {
            if (in_stack_00000004 == -0x7ffd773b) {
              return (int)"TYPE_E_SIZETOOBIG";
            }
            if (in_stack_00000004 < -0x7ffefeef) {
              if (in_stack_00000004 == -0x7ffefef0) {
                return (int)"RPC_E_VERSION_MISMATCH";
              }
              if (in_stack_00000004 < -0x7fffbfd6) {
                if (in_stack_00000004 == -0x7fffbfd7) {
                  return (int)"CO_E_ASYNC_WORK_REJECTED";
                }
                if (in_stack_00000004 < -0x7fffbfeb) {
                  if (in_stack_00000004 == -0x7fffbfec) {
                    return (int)"CO_E_BAD_SERVER_NAME";
                  }
                  if (in_stack_00000004 < -0x7fffbff5) {
                    if (in_stack_00000004 == -0x7fffbff6) {
                      return (int)"CO_E_INIT_RPC_CHANNEL";
                    }
                    if (in_stack_00000004 < -0x7fffbffa) {
                      if (in_stack_00000004 == -0x7fffbffb) {
                        return (int)"E_FAIL";
                      }
                      if (in_stack_00000004 == -0x7ffffff6) {
                        return (int)"E_PENDING";
                      }
                      if (in_stack_00000004 == -0x7fffbfff) {
                        return (int)"E_NOTIMPL";
                      }
                      if (in_stack_00000004 == -0x7fffbffe) {
                        return (int)"E_NOINTERFACE";
                      }
                      if (in_stack_00000004 == -0x7fffbffd) {
                        return (int)"E_POINTER";
                      }
                      if (in_stack_00000004 == -0x7fffbffc) {
                        return (int)"E_ABORT";
                      }
                    }
                    else {
                      if (in_stack_00000004 == -0x7fffbffa) {
                        return (int)"CO_E_INIT_TLS";
                      }
                      if (in_stack_00000004 == -0x7fffbff9) {
                        return (int)"CO_E_INIT_SHARED_ALLOCATOR";
                      }
                      if (in_stack_00000004 == -0x7fffbff8) {
                        return (int)"CO_E_INIT_MEMORY_ALLOCATOR";
                      }
                      if (in_stack_00000004 == -0x7fffbff7) {
                        return (int)"CO_E_INIT_CLASS_CACHE";
                      }
                    }
                  }
                  else {
                    switch(in_stack_00000004) {
                    case -0x7fffbff5:
                      return (int)"CO_E_INIT_TLS_SET_CHANNEL_CONTROL";
                    case -0x7fffbff4:
                      return (int)"CO_E_INIT_TLS_CHANNEL_CONTROL";
                    case -0x7fffbff3:
                      return (int)"CO_E_INIT_UNACCEPTED_USER_ALLOCATOR";
                    case -0x7fffbff2:
                      return (int)"CO_E_INIT_SCM_MUTEX_EXISTS";
                    case -0x7fffbff1:
                      return (int)"CO_E_INIT_SCM_FILE_MAPPING_EXISTS";
                    case -0x7fffbff0:
                      return (int)"CO_E_INIT_SCM_MAP_VIEW_OF_FILE";
                    case -0x7fffbfef:
                      return (int)"CO_E_INIT_SCM_EXEC_FAILURE";
                    case -0x7fffbfee:
                      return (int)"CO_E_INIT_ONLY_SINGLE_THREADED";
                    case -0x7fffbfed:
                      return (int)"CO_E_CANT_REMOTE";
                    }
                  }
                }
                else {
                  switch(in_stack_00000004) {
                  case -0x7fffbfeb:
                    return (int)"CO_E_WRONG_SERVER_IDENTITY";
                  case -0x7fffbfea:
                    return (int)"CO_E_OLE1DDE_DISABLED";
                  case -0x7fffbfe9:
                    return (int)"CO_E_RUNAS_SYNTAX";
                  case -0x7fffbfe8:
                    return (int)"CO_E_CREATEPROCESS_FAILURE";
                  case -0x7fffbfe7:
                    return (int)"CO_E_RUNAS_CREATEPROCESS_FAILURE";
                  case -0x7fffbfe6:
                    return (int)"CO_E_RUNAS_LOGON_FAILURE";
                  case -0x7fffbfe5:
                    return (int)"CO_E_LAUNCH_PERMSSION_DENIED";
                  case -0x7fffbfe4:
                    return (int)"CO_E_START_SERVICE_FAILURE";
                  case -0x7fffbfe3:
                    return (int)"CO_E_REMOTE_COMMUNICATION_FAILURE";
                  case -0x7fffbfe2:
                    return (int)"CO_E_SERVER_START_TIMEOUT";
                  case -0x7fffbfe1:
                    return (int)"CO_E_CLSREG_INCONSISTENT";
                  case -0x7fffbfe0:
                    return (int)"CO_E_IIDREG_INCONSISTENT";
                  case -0x7fffbfdf:
                    return (int)"CO_E_NOT_SUPPORTED";
                  case -0x7fffbfde:
                    return (int)"CO_E_RELOAD_DLL";
                  case -0x7fffbfdd:
                    return (int)"CO_E_MSI_ERROR";
                  case -0x7fffbfdc:
                    return (int)"CO_E_ATTEMPT_TO_CREATE_OUTSIDE_CLIENT_CONTEXT";
                  case -0x7fffbfdb:
                    return (int)"CO_E_SERVER_PAUSED";
                  case -0x7fffbfda:
                    return (int)"CO_E_SERVER_NOT_PAUSED";
                  case -0x7fffbfd9:
                    return (int)"CO_E_CLASS_DISABLED";
                  case -0x7fffbfd8:
                    return (int)"CO_E_CLRNOTAVAILABLE";
                  }
                }
              }
              else if (in_stack_00000004 < -0x7ffefff1) {
                if (in_stack_00000004 == -0x7ffefff2) {
                  return (int)"RPC_E_SERVER_CANTUNMARSHAL_DATA";
                }
                if (in_stack_00000004 < -0x7ffefffb) {
                  if (in_stack_00000004 == -0x7ffefffc) {
                    return (int)"RPC_E_CANTCALLOUT_INASYNCCALL";
                  }
                  if (in_stack_00000004 < -0x7fffbfcc) {
                    if (in_stack_00000004 == -0x7fffbfcd) {
                      return (int)"CO_E_MALFORMED_SPN";
                    }
                    if (in_stack_00000004 == -0x7fffbfd6) {
                      return (int)"CO_E_SERVER_INIT_TIMEOUT";
                    }
                    if (in_stack_00000004 == -0x7fffbfd5) {
                      return (int)"CO_E_NO_SECCTX_IN_ACTIVATE";
                    }
                    if (in_stack_00000004 == -0x7fffbfd0) {
                      return (int)"CO_E_TRACKER_CONFIG";
                    }
                    if (in_stack_00000004 == -0x7fffbfcf) {
                      return (int)"CO_E_THREADPOOL_CONFIG";
                    }
                    if (in_stack_00000004 == -0x7fffbfce) {
                      return (int)"CO_E_SXS_CONFIG";
                    }
                  }
                  else {
                    if (in_stack_00000004 == -0x7fff0001) {
                      return (int)"E_UNEXPECTED";
                    }
                    if (in_stack_00000004 == -0x7ffeffff) {
                      return (int)"RPC_E_CALL_REJECTED";
                    }
                    if (in_stack_00000004 == -0x7ffefffe) {
                      return (int)"RPC_E_CALL_CANCELED";
                    }
                    if (in_stack_00000004 == -0x7ffefffd) {
                      return (int)"RPC_E_CANTPOST_INSENDCALL";
                    }
                  }
                }
                else {
                  switch(in_stack_00000004) {
                  case -0x7ffefffb:
                    return (int)"RPC_E_CANTCALLOUT_INEXTERNALCALL";
                  case -0x7ffefffa:
                    return (int)"RPC_E_CONNECTION_TERMINATED";
                  case -0x7ffefff9:
                    return (int)"RPC_E_SERVER_DIED";
                  case -0x7ffefff8:
                    return (int)"RPC_E_CLIENT_DIED";
                  case -0x7ffefff7:
                    return (int)"RPC_E_INVALID_DATAPACKET";
                  case -0x7ffefff6:
                    return (int)"RPC_E_CANTTRANSMIT_CALL";
                  case -0x7ffefff5:
                    return (int)"RPC_E_CLIENT_CANTMARSHAL_DATA";
                  case -0x7ffefff4:
                    return (int)"RPC_E_CLIENT_CANTUNMARSHAL_DATA";
                  case -0x7ffefff3:
                    return (int)"RPC_E_SERVER_CANTMARSHAL_DATA";
                  }
                }
              }
              else if (in_stack_00000004 < -0x7ffefef9) {
                if (in_stack_00000004 == -0x7ffefefa) {
                  return (int)"RPC_E_CHANGED_MODE";
                }
                if (in_stack_00000004 < -0x7ffefefe) {
                  if (in_stack_00000004 == -0x7ffefeff) {
                    return (int)"RPC_E_OUT_OF_RESOURCES";
                  }
                  if (in_stack_00000004 == -0x7ffefff1) {
                    return (int)"RPC_E_INVALID_DATA";
                  }
                  if (in_stack_00000004 == -0x7ffefff0) {
                    return (int)"RPC_E_INVALID_PARAMETER";
                  }
                  if (in_stack_00000004 == -0x7ffeffef) {
                    return (int)"RPC_E_CANTCALLOUT_AGAIN";
                  }
                  if (in_stack_00000004 == -0x7ffeffee) {
                    return (int)"RPC_E_SERVER_DIED_DNE";
                  }
                  if (in_stack_00000004 == -0x7ffeff00) {
                    return (int)"RPC_E_SYS_CALL_FAILED";
                  }
                }
                else {
                  if (in_stack_00000004 == -0x7ffefefe) {
                    return (int)"RPC_E_ATTEMPTED_MULTITHREAD";
                  }
                  if (in_stack_00000004 == -0x7ffefefd) {
                    return (int)"RPC_E_NOT_REGISTERED";
                  }
                  if (in_stack_00000004 == -0x7ffefefc) {
                    return (int)"RPC_E_FAULT";
                  }
                  if (in_stack_00000004 == -0x7ffefefb) {
                    return (int)"RPC_E_SERVERFAULT";
                  }
                }
              }
              else {
                switch(in_stack_00000004) {
                case -0x7ffefef9:
                  return (int)"RPC_E_INVALIDMETHOD";
                case -0x7ffefef8:
                  return (int)"RPC_E_DISCONNECTED";
                case -0x7ffefef7:
                  return (int)"RPC_E_RETRY";
                case -0x7ffefef6:
                  return (int)"RPC_E_SERVERCALL_RETRYLATER";
                case -0x7ffefef5:
                  return (int)"RPC_E_SERVERCALL_REJECTED";
                case -0x7ffefef4:
                  return (int)"RPC_E_INVALID_CALLDATA";
                case -0x7ffefef3:
                  return (int)"RPC_E_CANTCALLOUT_ININPUTSYNCCALL";
                case -0x7ffefef2:
                  return (int)"RPC_E_WRONG_THREAD";
                case -0x7ffefef1:
                  return (int)"RPC_E_THREAD_NOT_INIT";
                }
              }
            }
            else if (in_stack_00000004 < -0x7ffe0000) {
              if (in_stack_00000004 == -0x7ffe0001) {
                return (int)"RPC_E_UNEXPECTED";
              }
              switch(in_stack_00000004) {
              case -0x7ffefeef:
                return (int)"RPC_E_INVALID_HEADER";
              case -0x7ffefeee:
                return (int)"RPC_E_INVALID_EXTENSION";
              case -0x7ffefeed:
                return (int)"RPC_E_INVALID_IPID";
              case -0x7ffefeec:
                return (int)"RPC_E_INVALID_OBJECT";
              case -0x7ffefeeb:
                return (int)"RPC_S_CALLPENDING";
              case -0x7ffefeea:
                return (int)"RPC_S_WAITONTIMER";
              case -0x7ffefee9:
                return (int)"RPC_E_CALL_COMPLETE";
              case -0x7ffefee8:
                return (int)"RPC_E_UNSECURE_CALL";
              case -0x7ffefee7:
                return (int)"RPC_E_TOO_LATE";
              case -0x7ffefee6:
                return (int)"RPC_E_NO_GOOD_SECURITY_PACKAGES";
              case -0x7ffefee5:
                return (int)"RPC_E_ACCESS_DENIED";
              case -0x7ffefee4:
                return (int)"RPC_E_REMOTE_DISABLED";
              case -0x7ffefee3:
                return (int)"RPC_E_INVALID_OBJREF";
              case -0x7ffefee2:
                return (int)"RPC_E_NO_CONTEXT";
              case -0x7ffefee1:
                return (int)"RPC_E_TIMEOUT";
              case -0x7ffefee0:
                return (int)"RPC_E_NO_SYNC";
              case -0x7ffefedf:
                return (int)"RPC_E_FULLSIC_REQUIRED";
              case -0x7ffefede:
                return (int)"RPC_E_INVALID_STD_NAME";
              case -0x7ffefedd:
                return (int)"CO_E_FAILEDTOIMPERSONATE";
              case -0x7ffefedc:
                return (int)"CO_E_FAILEDTOGETSECCTX";
              case -0x7ffefedb:
                return (int)"CO_E_FAILEDTOOPENTHREADTOKEN";
              case -0x7ffefeda:
                return (int)"CO_E_FAILEDTOGETTOKENINFO";
              case -0x7ffefed9:
                return (int)"CO_E_TRUSTEEDOESNTMATCHCLIENT";
              case -0x7ffefed8:
                return (int)"CO_E_FAILEDTOQUERYCLIENTBLANKET";
              case -0x7ffefed7:
                return (int)"CO_E_FAILEDTOSETDACL";
              case -0x7ffefed6:
                return (int)"CO_E_ACCESSCHECKFAILED";
              case -0x7ffefed5:
                return (int)"CO_E_NETACCESSAPIFAILED";
              case -0x7ffefed4:
                return (int)"CO_E_WRONGTRUSTEENAMESYNTAX";
              case -0x7ffefed3:
                return (int)"CO_E_INVALIDSID";
              case -0x7ffefed2:
                return (int)"CO_E_CONVERSIONFAILED";
              case -0x7ffefed1:
                return (int)"CO_E_NOMATCHINGSIDFOUND";
              case -0x7ffefed0:
                return (int)"CO_E_LOOKUPACCSIDFAILED";
              case -0x7ffefecf:
                return (int)"CO_E_NOMATCHINGNAMEFOUND";
              case -0x7ffefece:
                return (int)"CO_E_LOOKUPACCNAMEFAILED";
              case -0x7ffefecd:
                return (int)"CO_E_SETSERLHNDLFAILED";
              case -0x7ffefecc:
                return (int)"CO_E_FAILEDTOGETWINDIR";
              case -0x7ffefecb:
                return (int)"CO_E_PATHTOOLONG";
              case -0x7ffefeca:
                return (int)"CO_E_FAILEDTOGENUUID";
              case -0x7ffefec9:
                return (int)"CO_E_FAILEDTOCREATEFILE";
              case -0x7ffefec8:
                return (int)"CO_E_FAILEDTOCLOSEHANDLE";
              case -0x7ffefec7:
                return (int)"CO_E_EXCEEDSYSACLLIMIT";
              case -0x7ffefec6:
                return (int)"CO_E_ACESINWRONGORDER";
              case -0x7ffefec5:
                return (int)"CO_E_INCOMPATIBLESTREAMVERSION";
              case -0x7ffefec4:
                return (int)"CO_E_FAILEDTOOPENPROCESSTOKEN";
              case -0x7ffefec3:
                return (int)"CO_E_DECODEFAILED";
              case -0x7ffefec1:
                return (int)"CO_E_ACNOTINITIALIZED";
              case -0x7ffefec0:
                return (int)"CO_E_CANCEL_DISABLED";
              }
            }
            else if (in_stack_00000004 < -0x7ffd7fe9) {
              if (in_stack_00000004 == -0x7ffd7fea) {
                return (int)"TYPE_E_BUFFERTOOSMALL";
              }
              switch(in_stack_00000004) {
              case -0x7ffdffff:
                return (int)"DISP_E_UNKNOWNINTERFACE";
              case -0x7ffdfffd:
                return (int)"DISP_E_MEMBERNOTFOUND";
              case -0x7ffdfffc:
                return (int)"DISP_E_PARAMNOTFOUND";
              case -0x7ffdfffb:
                return (int)"DISP_E_TYPEMISMATCH";
              case -0x7ffdfffa:
                return (int)"DISP_E_UNKNOWNNAME";
              case -0x7ffdfff9:
                return (int)"DISP_E_NONAMEDARGS";
              case -0x7ffdfff8:
                return (int)"DISP_E_BADVARTYPE";
              case -0x7ffdfff7:
                return (int)"DISP_E_EXCEPTION";
              case -0x7ffdfff6:
                return (int)"DISP_E_OVERFLOW";
              case -0x7ffdfff5:
                return (int)"DISP_E_BADINDEX";
              case -0x7ffdfff4:
                return (int)"DISP_E_UNKNOWNLCID";
              case -0x7ffdfff3:
                return (int)"DISP_E_ARRAYISLOCKED";
              case -0x7ffdfff2:
                return (int)"DISP_E_BADPARAMCOUNT";
              case -0x7ffdfff1:
                return (int)"DISP_E_PARAMNOTOPTIONAL";
              case -0x7ffdfff0:
                return (int)"DISP_E_BADCALLEE";
              case -0x7ffdffef:
                return (int)"DISP_E_NOTACOLLECTION";
              case -0x7ffdffee:
                return (int)"DISP_E_DIVBYZERO";
              case -0x7ffdffed:
                return (int)"DISP_E_BUFFERTOOSMALL";
              }
            }
            else if (in_stack_00000004 < -0x7ffd7fd6) {
              if (in_stack_00000004 == -0x7ffd7fd7) {
                return (int)"TYPE_E_INVALIDSTATE";
              }
              if (in_stack_00000004 == -0x7ffd7fe9) {
                return (int)"TYPE_E_FIELDNOTFOUND";
              }
              if (in_stack_00000004 == -0x7ffd7fe8) {
                return (int)"TYPE_E_INVDATAREAD";
              }
              if (in_stack_00000004 == -0x7ffd7fe7) {
                return (int)"TYPE_E_UNSUPFORMAT";
              }
              if (in_stack_00000004 == -0x7ffd7fe4) {
                return (int)"TYPE_E_REGISTRYACCESS";
              }
              if (in_stack_00000004 == -0x7ffd7fe3) {
                return (int)"TYPE_E_LIBNOTREGISTERED";
              }
              if (in_stack_00000004 == -0x7ffd7fd9) {
                return (int)"TYPE_E_UNDEFINEDTYPE";
              }
              if (in_stack_00000004 == -0x7ffd7fd8) {
                return (int)"TYPE_E_QUALIFIEDNAMEDISALLOWED";
              }
            }
            else {
              if (in_stack_00000004 == -0x7ffd7fd6) {
                return (int)"TYPE_E_WRONGTYPEKIND";
              }
              if (in_stack_00000004 == -0x7ffd7fd5) {
                return (int)"TYPE_E_ELEMENTNOTFOUND";
              }
              if (in_stack_00000004 == -0x7ffd7fd4) {
                return (int)"TYPE_E_AMBIGUOUSNAME";
              }
              if (in_stack_00000004 == -0x7ffd7fd3) {
                return (int)"TYPE_E_NAMECONFLICT";
              }
              if (in_stack_00000004 == -0x7ffd7fd2) {
                return (int)"TYPE_E_UNKNOWNLCID";
              }
              if (in_stack_00000004 == -0x7ffd7fd1) {
                return (int)"TYPE_E_DLLFUNCTIONNOTFOUND";
              }
              if (in_stack_00000004 == -0x7ffd7743) {
                return (int)"TYPE_E_BADMODULEKIND";
              }
            }
          }
          else if (in_stack_00000004 < -0x7ffbff94) {
            if (in_stack_00000004 == -0x7ffbff95) {
              return (int)"DV_E_DVASPECT";
            }
            if (in_stack_00000004 < -0x7ffcfef8) {
              if (in_stack_00000004 == -0x7ffcfef9) {
                return (int)"STG_E_NOTFILEBASEDSTORAGE";
              }
              if (in_stack_00000004 < -0x7ffcffe2) {
                if (in_stack_00000004 == -0x7ffcffe3) {
                  return (int)"STG_E_WRITEFAULT";
                }
                if (in_stack_00000004 < -0x7ffcfffd) {
                  if (in_stack_00000004 == -0x7ffcfffe) {
                    return (int)"STG_E_FILENOTFOUND";
                  }
                  if (in_stack_00000004 < -0x7ffd735c) {
                    if (in_stack_00000004 == -0x7ffd735d) {
                      return (int)"TYPE_E_CANTCREATETMPFILE";
                    }
                    if (in_stack_00000004 == -0x7ffd773a) {
                      return (int)"TYPE_E_DUPLICATEID";
                    }
                    if (in_stack_00000004 == -0x7ffd7731) {
                      return (int)"TYPE_E_INVALIDID";
                    }
                    if (in_stack_00000004 == -0x7ffd7360) {
                      return (int)"TYPE_E_TYPEMISMATCH";
                    }
                    if (in_stack_00000004 == -0x7ffd735f) {
                      return (int)"TYPE_E_OUTOFBOUNDS";
                    }
                    if (in_stack_00000004 == -0x7ffd735e) {
                      return (int)"TYPE_E_IOERROR";
                    }
                  }
                  else {
                    if (in_stack_00000004 == -0x7ffd63b6) {
                      return (int)"TYPE_E_CANTLOADLIBRARY";
                    }
                    if (in_stack_00000004 == -0x7ffd637d) {
                      return (int)"TYPE_E_INCONSISTENTPROPFUNCS";
                    }
                    if (in_stack_00000004 == -0x7ffd637c) {
                      return (int)"TYPE_E_CIRCULARTYPE";
                    }
                    if (in_stack_00000004 == -0x7ffcffff) {
                      return (int)"STG_E_INVALIDFUNCTION";
                    }
                  }
                }
                else {
                  switch(in_stack_00000004) {
                  case -0x7ffcfffd:
                    return (int)"STG_E_PATHNOTFOUND";
                  case -0x7ffcfffc:
                    return (int)"STG_E_TOOMANYOPENFILES";
                  case -0x7ffcfffb:
                    return (int)"STG_E_ACCESSDENIED";
                  case -0x7ffcfffa:
                    return (int)"STG_E_INVALIDHANDLE";
                  case -0x7ffcfff8:
                    return (int)"STG_E_INSUFFICIENTMEMORY";
                  case -0x7ffcfff7:
                    return (int)"STG_E_INVALIDPOINTER";
                  case -0x7ffcffee:
                    return (int)"STG_E_NOMOREFILES";
                  case -0x7ffcffed:
                    return (int)"STG_E_DISKISWRITEPROTECTED";
                  case -0x7ffcffe7:
                    return (int)"STG_E_SEEKERROR";
                  }
                }
              }
              else if (in_stack_00000004 < -0x7ffcff02) {
                if (in_stack_00000004 == -0x7ffcff03) {
                  return (int)"STG_E_UNKNOWN";
                }
                if (in_stack_00000004 < -0x7ffcff8f) {
                  if (in_stack_00000004 == -0x7ffcff90) {
                    return (int)"STG_E_MEDIUMFULL";
                  }
                  if (in_stack_00000004 == -0x7ffcffe2) {
                    return (int)"STG_E_READFAULT";
                  }
                  if (in_stack_00000004 == -0x7ffcffe0) {
                    return (int)"STG_E_SHAREVIOLATION";
                  }
                  if (in_stack_00000004 == -0x7ffcffdf) {
                    return (int)"STG_E_LOCKVIOLATION";
                  }
                  if (in_stack_00000004 == -0x7ffcffb0) {
                    return (int)"STG_E_FILEALREADYEXISTS";
                  }
                  if (in_stack_00000004 == -0x7ffcffa9) {
                    return (int)"STG_E_INVALIDPARAMETER";
                  }
                }
                else {
                  if (in_stack_00000004 == -0x7ffcff10) {
                    return (int)"STG_E_PROPSETMISMATCHED";
                  }
                  if (in_stack_00000004 == -0x7ffcff06) {
                    return (int)"STG_E_ABNORMALAPIEXIT";
                  }
                  if (in_stack_00000004 == -0x7ffcff05) {
                    return (int)"STG_E_INVALIDHEADER";
                  }
                  if (in_stack_00000004 == -0x7ffcff04) {
                    return (int)"STG_E_INVALIDNAME";
                  }
                }
              }
              else {
                switch(in_stack_00000004) {
                case -0x7ffcff02:
                  return (int)"STG_E_UNIMPLEMENTEDFUNCTION";
                case -0x7ffcff01:
                  return (int)"STG_E_INVALIDFLAG";
                case -0x7ffcff00:
                  return (int)"STG_E_INUSE";
                case -0x7ffcfeff:
                  return (int)"STG_E_NOTCURRENT";
                case -0x7ffcfefe:
                  return (int)"STG_E_REVERTED";
                case -0x7ffcfefd:
                  return (int)"STG_E_CANTSAVE";
                case -0x7ffcfefc:
                  return (int)"STG_E_OLDFORMAT";
                case -0x7ffcfefb:
                  return (int)"STG_E_OLDDLL";
                case -0x7ffcfefa:
                  return (int)"STG_E_SHAREREQUIRED";
                }
              }
            }
            else if (in_stack_00000004 < -0x7ffbfff9) {
              if (in_stack_00000004 == -0x7ffbfffa) {
                return (int)"OLE_E_NOCACHE";
              }
              if (in_stack_00000004 < -0x7ffcfcf7) {
                if (in_stack_00000004 == -0x7ffcfcf8) {
                  return (int)"STG_E_CSS_KEY_NOT_ESTABLISHED";
                }
                if (in_stack_00000004 < -0x7ffcfdfe) {
                  if (in_stack_00000004 == -0x7ffcfdff) {
                    return (int)"STG_E_INCOMPLETE";
                  }
                  if (in_stack_00000004 == -0x7ffcfef8) {
                    return (int)"STG_E_EXTANTMARSHALLINGS";
                  }
                  if (in_stack_00000004 == -0x7ffcfef7) {
                    return (int)"STG_E_DOCFILECORRUPT";
                  }
                  if (in_stack_00000004 == -0x7ffcfef0) {
                    return (int)"STG_E_BADBASEADDRESS";
                  }
                  if (in_stack_00000004 == -0x7ffcfeef) {
                    return (int)"STG_E_DOCFILETOOLARGE";
                  }
                  if (in_stack_00000004 == -0x7ffcfeee) {
                    return (int)"STG_E_NOTSIMPLEFORMAT";
                  }
                }
                else {
                  if (in_stack_00000004 == -0x7ffcfdfe) {
                    return (int)"STG_E_TERMINATED";
                  }
                  if (in_stack_00000004 == -0x7ffcfcfb) {
                    return (int)"STG_E_STATUS_COPY_PROTECTION_FAILURE";
                  }
                  if (in_stack_00000004 == -0x7ffcfcfa) {
                    return (int)"STG_E_CSS_AUTHENTICATION_FAILURE";
                  }
                  if (in_stack_00000004 == -0x7ffcfcf9) {
                    return (int)"STG_E_CSS_KEY_NOT_PRESENT";
                  }
                }
              }
              else if (in_stack_00000004 < -0x7ffbfffe) {
                if (in_stack_00000004 == -0x7ffbffff) {
                  return (int)"OLE_E_ADVF";
                }
                if (in_stack_00000004 == -0x7ffcfcf7) {
                  return (int)"STG_E_CSS_SCRAMBLED_SECTOR";
                }
                if (in_stack_00000004 == -0x7ffcfcf6) {
                  return (int)"STG_E_CSS_REGION_MISMATCH";
                }
                if (in_stack_00000004 == -0x7ffcfcf5) {
                  return (int)"STG_E_RESETS_EXHAUSTED";
                }
                if (in_stack_00000004 == -0x7ffc0000) {
                  return (int)"OLE_E_FIRST";
                }
              }
              else {
                if (in_stack_00000004 == -0x7ffbfffe) {
                  return (int)"OLE_E_ENUM_NOMORE";
                }
                if (in_stack_00000004 == -0x7ffbfffd) {
                  return (int)"OLE_E_ADVISENOTSUPPORTED";
                }
                if (in_stack_00000004 == -0x7ffbfffc) {
                  return (int)"OLE_E_NOCONNECTION";
                }
                if (in_stack_00000004 == -0x7ffbfffb) {
                  return (int)"OLE_E_NOTRUNNING";
                }
              }
            }
            else if (in_stack_00000004 < -0x7ffbff9b) {
              if (in_stack_00000004 == -0x7ffbff9c) {
                return (int)"DV_E_FORMATETC";
              }
              switch(in_stack_00000004) {
              case -0x7ffbfff9:
                return (int)"OLE_E_BLANK";
              case -0x7ffbfff8:
                return (int)"OLE_E_CLASSDIFF";
              case -0x7ffbfff7:
                return (int)"OLE_E_CANT_GETMONIKER";
              case -0x7ffbfff6:
                return (int)"OLE_E_CANT_BINDTOSOURCE";
              case -0x7ffbfff5:
                return (int)"OLE_E_STATIC";
              case -0x7ffbfff4:
                return (int)"OLE_E_PROMPTSAVECANCELLED";
              case -0x7ffbfff3:
                return (int)"OLE_E_INVALIDRECT";
              case -0x7ffbfff2:
                return (int)"OLE_E_WRONGCOMPOBJ";
              case -0x7ffbfff1:
                return (int)"OLE_E_INVALIDHWND";
              case -0x7ffbfff0:
                return (int)"OLE_E_NOT_INPLACEACTIVE";
              case -0x7ffbffef:
                return (int)"OLE_E_CANTCONVERT";
              case -0x7ffbffee:
                return (int)"OLE_E_NOSTORAGE";
              }
            }
            else {
              if (in_stack_00000004 == -0x7ffbff9b) {
                return (int)"DV_E_DVTARGETDEVICE";
              }
              if (in_stack_00000004 == -0x7ffbff9a) {
                return (int)"DV_E_STGMEDIUM";
              }
              if (in_stack_00000004 == -0x7ffbff99) {
                return (int)"DV_E_STATDATA";
              }
              if (in_stack_00000004 == -0x7ffbff98) {
                return (int)"DV_E_LINDEX";
              }
              if (in_stack_00000004 == -0x7ffbff97) {
                return (int)"DV_E_TYMED";
              }
              if (in_stack_00000004 == -0x7ffbff96) {
                return (int)"DV_E_CLIPFORMAT";
              }
            }
          }
          else if (in_stack_00000004 < -0x7ffbfe7f) {
            if (in_stack_00000004 == -0x7ffbfe80) {
              return (int)"OLEOBJ_E_FIRST";
            }
            if (in_stack_00000004 < -0x7ffbfeac) {
              if (in_stack_00000004 == -0x7ffbfead) {
                return (int)"REGDB_E_INVALIDVALUE";
              }
              if (in_stack_00000004 < -0x7ffbfee0) {
                if (in_stack_00000004 == -0x7ffbfee1) {
                  return (int)"CLASSFACTORY_E_LAST";
                }
                if (in_stack_00000004 < -0x7ffbfefd) {
                  if (in_stack_00000004 == -0x7ffbfefe) {
                    return (int)"DRAGDROP_E_INVALIDHWND";
                  }
                  if (in_stack_00000004 == -0x7ffbff94) {
                    return (int)"DV_E_DVTARGETDEVICE_SIZE";
                  }
                  if (in_stack_00000004 == -0x7ffbff93) {
                    return (int)"DV_E_NOIVIEWOBJECT";
                  }
                  if (in_stack_00000004 == -0x7ffbff01) {
                    return (int)"OLE_E_LAST";
                  }
                  if (in_stack_00000004 == -0x7ffbff00) {
                    return (int)"DRAGDROP_E_FIRST";
                  }
                  if (in_stack_00000004 == -0x7ffbfeff) {
                    return (int)"DRAGDROP_E_ALREADYREGISTERED";
                  }
                }
                else {
                  if (in_stack_00000004 == -0x7ffbfef1) {
                    return (int)"DRAGDROP_E_LAST";
                  }
                  if (in_stack_00000004 == -0x7ffbfef0) {
                    return (int)"CLASSFACTORY_E_FIRST";
                  }
                  if (in_stack_00000004 == -0x7ffbfeef) {
                    return (int)"CLASS_E_CLASSNOTAVAILABLE";
                  }
                  if (in_stack_00000004 == -0x7ffbfeee) {
                    return (int)"CLASS_E_NOTLICENSED";
                  }
                }
              }
              else if (in_stack_00000004 < -0x7ffbfebf) {
                if (in_stack_00000004 == -0x7ffbfec0) {
                  return (int)"VIEW_E_FIRST";
                }
                if (in_stack_00000004 == -0x7ffbfee0) {
                  return (int)"MARSHAL_E_FIRST";
                }
                if (in_stack_00000004 == -0x7ffbfed1) {
                  return (int)"MARSHAL_E_LAST";
                }
                if (in_stack_00000004 == -0x7ffbfed0) {
                  return (int)"DATA_E_FIRST";
                }
                if (in_stack_00000004 == -0x7ffbfec1) {
                  return (int)"DATA_E_LAST";
                }
              }
              else {
                if (in_stack_00000004 == -0x7ffbfeb1) {
                  return (int)"VIEW_E_LAST";
                }
                if (in_stack_00000004 == -0x7ffbfeb0) {
                  return (int)"REGDB_E_FIRST";
                }
                if (in_stack_00000004 == -0x7ffbfeaf) {
                  return (int)"REGDB_E_WRITEREGDB";
                }
                if (in_stack_00000004 == -0x7ffbfeae) {
                  return (int)"REGDB_E_KEYMISSING";
                }
              }
            }
            else {
              switch(in_stack_00000004) {
              case -0x7ffbfeac:
                return (int)"REGDB_E_CLASSNOTREG";
              case -0x7ffbfeab:
                return (int)"REGDB_E_IIDNOTREG";
              case -0x7ffbfeaa:
                return (int)"REGDB_E_BADTHREADINGMODEL";
              case -0x7ffbfea1:
                return (int)"REGDB_E_LAST";
              case -0x7ffbfea0:
                return (int)"CAT_E_FIRST";
              case -0x7ffbfe9f:
                return (int)"CAT_E_LAST";
              case -0x7ffbfe9c:
                return (int)"CS_E_FIRST";
              case -0x7ffbfe9b:
                return (int)"CS_E_NOT_DELETABLE";
              case -0x7ffbfe9a:
                return (int)"CS_E_CLASS_NOTFOUND";
              case -0x7ffbfe99:
                return (int)"CS_E_INVALID_VERSION";
              case -0x7ffbfe98:
                return (int)"CS_E_NO_CLASSSTORE";
              case -0x7ffbfe97:
                return (int)"CS_E_OBJECT_NOTFOUND";
              case -0x7ffbfe96:
                return (int)"CS_E_OBJECT_ALREADY_EXISTS";
              case -0x7ffbfe95:
                return (int)"CS_E_INVALID_PATH";
              case -0x7ffbfe94:
                return (int)"CS_E_NETWORK_ERROR";
              case -0x7ffbfe93:
                return (int)"CS_E_ADMIN_LIMIT_EXCEEDED";
              case -0x7ffbfe92:
                return (int)"CS_E_SCHEMA_MISMATCH";
              case -0x7ffbfe91:
                return (int)"CS_E_LAST";
              case -0x7ffbfe90:
                return (int)"CACHE_E_FIRST";
              case -0x7ffbfe81:
                return (int)"CACHE_E_LAST";
              }
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7ffbfe7f:
              return (int)"OLEOBJ_E_INVALIDVERB";
            case -0x7ffbfe71:
              return (int)"OLEOBJ_E_LAST";
            case -0x7ffbfe70:
              return (int)"CLIENTSITE_E_FIRST";
            case -0x7ffbfe61:
              return (int)"CLIENTSITE_E_LAST";
            case -0x7ffbfe60:
              return (int)"INPLACE_E_NOTUNDOABLE";
            case -0x7ffbfe5f:
              return (int)"INPLACE_E_NOTOOLSPACE";
            case -0x7ffbfe51:
              return (int)"INPLACE_E_LAST";
            case -0x7ffbfe50:
              return (int)"ENUM_E_FIRST";
            case -0x7ffbfe41:
              return (int)"ENUM_E_LAST";
            case -0x7ffbfe40:
              return (int)"CONVERT10_E_FIRST";
            case -0x7ffbfe3f:
              return (int)"CONVERT10_E_OLESTREAM_PUT";
            case -0x7ffbfe3e:
              return (int)"CONVERT10_E_OLESTREAM_FMT";
            case -0x7ffbfe3d:
              return (int)"CONVERT10_E_OLESTREAM_BITMAP_TO_DIB";
            case -0x7ffbfe3c:
              return (int)"CONVERT10_E_STG_FMT";
            case -0x7ffbfe3b:
              return (int)"CONVERT10_E_STG_NO_STD_STREAM";
            case -0x7ffbfe3a:
              return (int)"CONVERT10_E_STG_DIB_TO_BITMAP";
            case -0x7ffbfe31:
              return (int)"CONVERT10_E_LAST";
            case -0x7ffbfe30:
              return (int)"CLIPBRD_E_FIRST";
            case -0x7ffbfe2f:
              return (int)"CLIPBRD_E_CANT_EMPTY";
            case -0x7ffbfe2e:
              return (int)"CLIPBRD_E_CANT_SET";
            case -0x7ffbfe2d:
              return (int)"CLIPBRD_E_BAD_DATA";
            case -0x7ffbfe2c:
              return (int)"CLIPBRD_E_CANT_CLOSE";
            case -0x7ffbfe21:
              return (int)"CLIPBRD_E_LAST";
            case -0x7ffbfe20:
              return (int)"MK_E_FIRST";
            case -0x7ffbfe1f:
              return (int)"MK_E_EXCEEDEDDEADLINE";
            case -0x7ffbfe1e:
              return (int)"MK_E_NEEDGENERIC";
            case -0x7ffbfe1d:
              return (int)"MK_E_UNAVAILABLE";
            case -0x7ffbfe1c:
              return (int)"MK_E_SYNTAX";
            case -0x7ffbfe1b:
              return (int)"MK_E_NOOBJECT";
            case -0x7ffbfe1a:
              return (int)"MK_E_INVALIDEXTENSION";
            case -0x7ffbfe19:
              return (int)"MK_E_INTERMEDIATEINTERFACENOTSUPPORTED";
            case -0x7ffbfe18:
              return (int)"MK_E_NOTBINDABLE";
            case -0x7ffbfe17:
              return (int)"MK_E_NOTBOUND";
            case -0x7ffbfe16:
              return (int)"MK_E_CANTOPENFILE";
            case -0x7ffbfe15:
              return (int)"MK_E_MUSTBOTHERUSER";
            case -0x7ffbfe14:
              return (int)"MK_E_NOINVERSE";
            case -0x7ffbfe13:
              return (int)"MK_E_NOSTORAGE";
            case -0x7ffbfe12:
              return (int)"MK_E_NOPREFIX";
            case -0x7ffbfe11:
              return (int)"MK_E_LAST";
            case -0x7ffbfe10:
              return (int)"CO_E_NOTINITIALIZED";
            }
          }
        }
        else if (in_stack_00000004 < -0x7ffbfc0d) {
          if (in_stack_00000004 == -0x7ffbfc0e) {
            return (int)"VFW_E_BAD_KEY";
          }
          switch(in_stack_00000004) {
          case -0x7ffbfe0e:
            return (int)"CO_E_CANTDETERMINECLASS";
          case -0x7ffbfe0d:
            return (int)"CO_E_CLASSSTRING";
          case -0x7ffbfe0c:
            return (int)"CO_E_IIDSTRING";
          case -0x7ffbfe0b:
            return (int)"CO_E_APPNOTFOUND";
          case -0x7ffbfe0a:
            return (int)"CO_E_APPSINGLEUSE";
          case -0x7ffbfe09:
            return (int)"CO_E_ERRORINAPP";
          case -0x7ffbfe08:
            return (int)"CO_E_DLLNOTFOUND";
          case -0x7ffbfe07:
            return (int)"CO_E_ERRORINDLL";
          case -0x7ffbfe06:
            return (int)"CO_E_WRONGOSFORAPP";
          case -0x7ffbfe05:
            return (int)"CO_E_OBJNOTREG";
          case -0x7ffbfe04:
            return (int)"CO_E_OBJISREG";
          case -0x7ffbfe03:
            return (int)"CO_E_OBJNOTCONNECTED";
          case -0x7ffbfe02:
            return (int)"CO_E_APPDIDNTREG";
          case -0x7ffbfe01:
            return (int)"CO_E_RELEASED";
          case -0x7ffbfe00:
            return (int)"DIERR_INSUFFICIENTPRIVS & VFW_E_INVALIDMEDIATYPE";
          case -0x7ffbfdff:
            return (int)"DIERR_DEVICEFULL & VFW_E_INVALIDSUBTYPE & DMO_E_INVALIDSTREAMINDEX";
          case -0x7ffbfdfe:
            return (int)"DIERR_MOREDATA & VFW_E_NEED_OWNER & DMO_E_INVALIDTYPE";
          case -0x7ffbfdfd:
            return (int)"DIERR_NOTDOWNLOADED & VFW_E_ENUM_OUT_OF_SYNC & DMO_E_TYPE_NOT_SET";
          case -0x7ffbfdfc:
            return (int)"DIERR_HASEFFECTS & VFW_E_ALREADY_CONNECTED & DMO_E_NOTACCEPTING";
          case -0x7ffbfdfb:
            return (int)"DIERR_NOTEXCLUSIVEACQUIRED & VFW_E_FILTER_ACTIVE & DMO_E_TYPE_NOT_ACCEPTED"
            ;
          case -0x7ffbfdfa:
            return (int)"DIERR_INCOMPLETEEFFECT & VFW_E_NO_TYPES & DMO_E_NO_MORE_ITEMS";
          case -0x7ffbfdf9:
            return (int)"DIERR_NOTBUFFERED & VFW_E_NO_ACCEPTABLE_TYPES";
          case -0x7ffbfdf8:
            return (int)"DIERR_EFFECTPLAYING & VFW_E_INVALID_DIRECTION";
          case -0x7ffbfdf7:
            return (int)"DIERR_UNPLUGGED & VFW_E_NOT_CONNECTED";
          case -0x7ffbfdf6:
            return (int)"DIERR_REPORTFULL & VFW_E_NO_ALLOCATOR";
          case -0x7ffbfdf5:
            return (int)"DIERR_MAPFILEFAIL & VFW_E_RUNTIME_ERROR";
          case -0x7ffbfdf4:
            return (int)"VFW_E_BUFFER_NOTSET";
          case -0x7ffbfdf3:
            return (int)"VFW_E_BUFFER_OVERFLOW";
          case -0x7ffbfdf2:
            return (int)"VFW_E_BADALIGN";
          case -0x7ffbfdf1:
            return (int)"VFW_E_ALREADY_COMMITTED";
          case -0x7ffbfdf0:
            return (int)"VFW_E_BUFFERS_OUTSTANDING";
          case -0x7ffbfdef:
            return (int)"VFW_E_NOT_COMMITTED";
          case -0x7ffbfdee:
            return (int)"VFW_E_SIZENOTSET";
          case -0x7ffbfded:
            return (int)"VFW_E_NO_CLOCK";
          case -0x7ffbfdec:
            return (int)"VFW_E_NO_SINK";
          case -0x7ffbfdeb:
            return (int)"VFW_E_NO_INTERFACE";
          case -0x7ffbfdea:
            return (int)"VFW_E_NOT_FOUND";
          case -0x7ffbfde9:
            return (int)"VFW_E_CANNOT_CONNECT";
          case -0x7ffbfde8:
            return (int)"VFW_E_CANNOT_RENDER";
          case -0x7ffbfde7:
            return (int)"VFW_E_CHANGING_FORMAT";
          case -0x7ffbfde6:
            return (int)"VFW_E_NO_COLOR_KEY_SET";
          case -0x7ffbfde5:
            return (int)"VFW_E_NOT_OVERLAY_CONNECTION";
          case -0x7ffbfde4:
            return (int)"VFW_E_NOT_SAMPLE_CONNECTION";
          case -0x7ffbfde3:
            return (int)"VFW_E_PALETTE_SET";
          case -0x7ffbfde2:
            return (int)"VFW_E_COLOR_KEY_SET";
          case -0x7ffbfde1:
            return (int)"VFW_E_NO_COLOR_KEY_FOUND";
          case -0x7ffbfde0:
            return (int)"VFW_E_NO_PALETTE_AVAILABLE";
          case -0x7ffbfddf:
            return (int)"VFW_E_NO_DISPLAY_PALETTE";
          case -0x7ffbfdde:
            return (int)"VFW_E_TOO_MANY_COLORS";
          case -0x7ffbfddd:
            return (int)"VFW_E_STATE_CHANGED";
          case -0x7ffbfddc:
            return (int)"VFW_E_NOT_STOPPED";
          case -0x7ffbfddb:
            return (int)"VFW_E_NOT_PAUSED";
          case -0x7ffbfdda:
            return (int)"VFW_E_NOT_RUNNING";
          case -0x7ffbfdd9:
            return (int)"VFW_E_WRONG_STATE";
          case -0x7ffbfdd8:
            return (int)"VFW_E_START_TIME_AFTER_END";
          case -0x7ffbfdd7:
            return (int)"VFW_E_INVALID_RECT";
          case -0x7ffbfdd6:
            return (int)"VFW_E_TYPE_NOT_ACCEPTED";
          case -0x7ffbfdd5:
            return (int)"VFW_E_SAMPLE_REJECTED";
          case -0x7ffbfdd4:
            return (int)"VFW_E_SAMPLE_REJECTED_EOS";
          case -0x7ffbfdd3:
            return (int)"VFW_E_DUPLICATE_NAME";
          case -0x7ffbfdd2:
            return (int)"VFW_E_TIMEOUT";
          case -0x7ffbfdd1:
            return (int)"VFW_E_INVALID_FILE_FORMAT";
          case -0x7ffbfdd0:
            return (int)"VFW_E_ENUM_OUT_OF_RANGE";
          case -0x7ffbfdcf:
            return (int)"VFW_E_CIRCULAR_GRAPH";
          case -0x7ffbfdce:
            return (int)"VFW_E_NOT_ALLOWED_TO_SAVE";
          case -0x7ffbfdcd:
            return (int)"VFW_E_TIME_ALREADY_PASSED";
          case -0x7ffbfdcc:
            return (int)"VFW_E_ALREADY_CANCELLED";
          case -0x7ffbfdcb:
            return (int)"VFW_E_CORRUPT_GRAPH_FILE";
          case -0x7ffbfdca:
            return (int)"VFW_E_ADVISE_ALREADY_SET";
          case -0x7ffbfdc8:
            return (int)"VFW_E_NO_MODEX_AVAILABLE";
          case -0x7ffbfdc7:
            return (int)"VFW_E_NO_ADVISE_SET";
          case -0x7ffbfdc6:
            return (int)"VFW_E_NO_FULLSCREEN";
          case -0x7ffbfdc5:
            return (int)"VFW_E_IN_FULLSCREEN_MODE";
          case -0x7ffbfdc0:
            return (int)"VFW_E_UNKNOWN_FILE_TYPE";
          case -0x7ffbfdbf:
            return (int)"VFW_E_CANNOT_LOAD_SOURCE_FILTER";
          case -0x7ffbfdbd:
            return (int)"VFW_E_FILE_TOO_SHORT";
          case -0x7ffbfdbc:
            return (int)"VFW_E_INVALID_FILE_VERSION";
          case -0x7ffbfdb9:
            return (int)"VFW_E_INVALID_CLSID";
          case -0x7ffbfdb8:
            return (int)"VFW_E_INVALID_MEDIA_TYPE";
          case -0x7ffbfdb7:
            return (int)"VFW_E_SAMPLE_TIME_NOT_SET";
          case -0x7ffbfdaf:
            return (int)"VFW_E_MEDIA_TIME_NOT_SET";
          case -0x7ffbfdae:
            return (int)"VFW_E_NO_TIME_FORMAT_SET";
          case -0x7ffbfdad:
            return (int)"VFW_E_MONO_AUDIO_HW";
          case -0x7ffbfdab:
            return (int)"VFW_E_NO_DECOMPRESSOR";
          case -0x7ffbfdaa:
            return (int)"VFW_E_NO_AUDIO_HARDWARE";
          case -0x7ffbfda7:
            return (int)"VFW_E_RPZA";
          case -0x7ffbfda5:
            return (int)"VFW_E_PROCESSOR_NOT_SUITABLE";
          case -0x7ffbfda4:
            return (int)"VFW_E_UNSUPPORTED_AUDIO";
          case -0x7ffbfda3:
            return (int)"VFW_E_UNSUPPORTED_VIDEO";
          case -0x7ffbfda2:
            return (int)"VFW_E_MPEG_NOT_CONSTRAINED";
          case -0x7ffbfda1:
            return (int)"VFW_E_NOT_IN_GRAPH";
          case -0x7ffbfd9f:
            return (int)"VFW_E_NO_TIME_FORMAT";
          case -0x7ffbfd9e:
            return (int)"VFW_E_READ_ONLY";
          case -0x7ffbfd9c:
            return (int)"VFW_E_BUFFER_UNDERFLOW";
          case -0x7ffbfd9b:
            return (int)"VFW_E_UNSUPPORTED_STREAM";
          case -0x7ffbfd9a:
            return (int)"VFW_E_NO_TRANSPORT";
          case -0x7ffbfd97:
            return (int)"VFW_E_BAD_VIDEOCD";
          case -0x7ffbfd8f:
            return (int)"VFW_E_OUT_OF_VIDEO_MEMORY";
          case -0x7ffbfd8e:
            return (int)"VFW_E_VP_NEGOTIATION_FAILED";
          case -0x7ffbfd8d:
            return (int)"VFW_E_DDRAW_CAPS_NOT_SUITABLE";
          case -0x7ffbfd8c:
            return (int)"VFW_E_NO_VP_HARDWARE";
          case -0x7ffbfd8b:
            return (int)"VFW_E_NO_CAPTURE_HARDWARE";
          case -0x7ffbfd8a:
            return (int)"VFW_E_DVD_OPERATION_INHIBITED";
          case -0x7ffbfd89:
            return (int)"VFW_E_DVD_INVALIDDOMAIN";
          case -0x7ffbfd88:
            return (int)"VFW_E_DVD_NO_BUTTON";
          case -0x7ffbfd87:
            return (int)"VFW_E_DVD_GRAPHNOTREADY";
          case -0x7ffbfd86:
            return (int)"VFW_E_DVD_RENDERFAIL";
          case -0x7ffbfd85:
            return (int)"VFW_E_DVD_DECNOTENOUGH";
          case -0x7ffbfd84:
            return (int)"VFW_E_DDRAW_VERSION_NOT_SUITABLE";
          case -0x7ffbfd83:
            return (int)"VFW_E_COPYPROT_FAILED";
          case -0x7ffbfd81:
            return (int)"VFW_E_TIME_EXPIRED";
          case -0x7ffbfd7f:
            return (int)"VFW_E_DVD_WRONG_SPEED";
          case -0x7ffbfd7e:
            return (int)"VFW_E_DVD_MENU_DOES_NOT_EXIST";
          case -0x7ffbfd7d:
            return (int)"VFW_E_DVD_CMD_CANCELLED";
          case -0x7ffbfd7c:
            return (int)"VFW_E_DVD_STATE_WRONG_VERSION";
          case -0x7ffbfd7b:
            return (int)"VFW_E_DVD_STATE_CORRUPT";
          case -0x7ffbfd7a:
            return (int)"VFW_E_DVD_STATE_WRONG_DISC";
          case -0x7ffbfd79:
            return (int)"VFW_E_DVD_INCOMPATIBLE_REGION";
          case -0x7ffbfd78:
            return (int)"VFW_E_DVD_NO_ATTRIBUTES";
          case -0x7ffbfd77:
            return (int)"VFW_E_DVD_NO_GOUP_PGC";
          case -0x7ffbfd76:
            return (int)"VFW_E_DVD_LOW_PARENTAL_LEVEL";
          case -0x7ffbfd75:
            return (int)"VFW_E_DVD_NOT_IN_KARAOKE_MODE";
          case -0x7ffbfd72:
            return (int)"VFW_E_FRAME_STEP_UNSUPPORTED";
          case -0x7ffbfd71:
            return (int)"VFW_E_DVD_STREAM_DISABLED";
          case -0x7ffbfd70:
            return (int)"VFW_E_DVD_TITLE_UNKNOWN";
          case -0x7ffbfd6f:
            return (int)"VFW_E_DVD_INVALID_DISC";
          case -0x7ffbfd6e:
            return (int)"VFW_E_DVD_NO_RESUME_INFORMATION";
          case -0x7ffbfd6d:
            return (int)"VFW_E_PIN_ALREADY_BLOCKED_ON_THIS_THREAD";
          case -0x7ffbfd6c:
            return (int)"VFW_E_PIN_ALREADY_BLOCKED";
          case -0x7ffbfd6b:
            return (int)"VFW_E_CERTIFICATION_FAILURE";
          case -0x7ffbfd00:
            return (int)"DIERR_DRIVERFIRST";
          case -0x7ffbfcff:
            return (int)"DIERR_DRIVERFIRST+1";
          case -0x7ffbfcfe:
            return (int)"DIERR_DRIVERFIRST+2";
          case -0x7ffbfcfd:
            return (int)"DIERR_DRIVERFIRST+3";
          case -0x7ffbfcfc:
            return (int)"DIERR_DRIVERFIRST+4";
          case -0x7ffbfcfb:
            return (int)"DIERR_DRIVERFIRST+5";
          }
        }
        else if (in_stack_00000004 < -0x7ffbecf6) {
          if (in_stack_00000004 == -0x7ffbecf7) {
            return (int)"SCHED_E_TRIGGER_NOT_FOUND";
          }
          switch(in_stack_00000004) {
          case -0x7ffbfc01:
            return (int)"DIERR_DRIVERLAST";
          case -0x7ffbfc00:
            return (int)"DIERR_INVALIDCLASSINSTALLER";
          case -0x7ffbfbff:
            return (int)"DIERR_CANCELLED & MS_E_SAMPLEALLOC";
          case -0x7ffbfbfe:
            return (int)"DIERR_BADINF & MS_E_PURPOSEID";
          case -0x7ffbfbfd:
            return (int)"MS_E_NOSTREAM";
          case -0x7ffbfbfc:
            return (int)"MS_E_NOSEEKING";
          case -0x7ffbfbfb:
            return (int)"MS_E_INCOMPATIBLE";
          case -0x7ffbfbfa:
            return (int)"MS_E_BUSY";
          case -0x7ffbfbf9:
            return (int)"MS_E_NOTINIT";
          case -0x7ffbfbf8:
            return (int)"MS_E_SOURCEALREADYDEFINED";
          case -0x7ffbfbf7:
            return (int)"MS_E_INVALIDSTREAMTYPE";
          case -0x7ffbfbf6:
            return (int)"MS_E_NOTRUNNING";
          }
        }
        else if (in_stack_00000004 < -0x7ffb2fff) {
          if (in_stack_00000004 == -0x7ffb3000) {
            return (int)"XACT_E_FIRST";
          }
          switch(in_stack_00000004) {
          case -0x7ffbecf6:
            return (int)"SCHED_E_TASK_NOT_READY";
          case -0x7ffbecf5:
            return (int)"SCHED_E_TASK_NOT_RUNNING";
          case -0x7ffbecf4:
            return (int)"SCHED_E_SERVICE_NOT_INSTALLED";
          case -0x7ffbecf3:
            return (int)"SCHED_E_CANNOT_OPEN_TASK";
          case -0x7ffbecf2:
            return (int)"SCHED_E_INVALID_TASK";
          case -0x7ffbecf1:
            return (int)"SCHED_E_ACCOUNT_INFORMATION_NOT_SET";
          case -0x7ffbecf0:
            return (int)"SCHED_E_ACCOUNT_NAME_NOT_FOUND";
          case -0x7ffbecef:
            return (int)"SCHED_E_ACCOUNT_DBASE_CORRUPT";
          case -0x7ffbecee:
            return (int)"SCHED_E_NO_SECURITY_SERVICES";
          case -0x7ffbeced:
            return (int)"SCHED_E_UNKNOWN_OBJECT_VERSION";
          case -0x7ffbecec:
            return (int)"SCHED_E_UNSUPPORTED_ACCOUNT_OPTION";
          case -0x7ffbeceb:
            return (int)"SCHED_E_SERVICE_NOT_RUNNING";
          }
        }
        else if (in_stack_00000004 < -0x7ffb2f7f) {
          if (in_stack_00000004 == -0x7ffb2f80) {
            return (int)"XACT_E_CLERKNOTFOUND";
          }
          switch(in_stack_00000004) {
          case -0x7ffb2fff:
            return (int)"XACT_E_CANTRETAIN";
          case -0x7ffb2ffe:
            return (int)"XACT_E_COMMITFAILED";
          case -0x7ffb2ffd:
            return (int)"XACT_E_COMMITPREVENTED";
          case -0x7ffb2ffc:
            return (int)"XACT_E_HEURISTICABORT";
          case -0x7ffb2ffb:
            return (int)"XACT_E_HEURISTICCOMMIT";
          case -0x7ffb2ffa:
            return (int)"XACT_E_HEURISTICDAMAGE";
          case -0x7ffb2ff9:
            return (int)"XACT_E_HEURISTICDANGER";
          case -0x7ffb2ff8:
            return (int)"XACT_E_ISOLATIONLEVEL";
          case -0x7ffb2ff7:
            return (int)"XACT_E_NOASYNC";
          case -0x7ffb2ff6:
            return (int)"XACT_E_NOENLIST";
          case -0x7ffb2ff5:
            return (int)"XACT_E_NOISORETAIN";
          case -0x7ffb2ff4:
            return (int)"XACT_E_NORESOURCE";
          case -0x7ffb2ff3:
            return (int)"XACT_E_NOTCURRENT";
          case -0x7ffb2ff2:
            return (int)"XACT_E_NOTRANSACTION";
          case -0x7ffb2ff1:
            return (int)"XACT_E_NOTSUPPORTED";
          case -0x7ffb2ff0:
            return (int)"XACT_E_UNKNOWNRMGRID";
          case -0x7ffb2fef:
            return (int)"XACT_E_WRONGSTATE";
          case -0x7ffb2fee:
            return (int)"XACT_E_WRONGUOW";
          case -0x7ffb2fed:
            return (int)"XACT_E_XTIONEXISTS";
          case -0x7ffb2fec:
            return (int)"XACT_E_NOIMPORTOBJECT";
          case -0x7ffb2feb:
            return (int)"XACT_E_INVALIDCOOKIE";
          case -0x7ffb2fea:
            return (int)"XACT_E_INDOUBT";
          case -0x7ffb2fe9:
            return (int)"XACT_E_NOTIMEOUT";
          case -0x7ffb2fe8:
            return (int)"XACT_E_ALREADYINPROGRESS";
          case -0x7ffb2fe7:
            return (int)"XACT_E_ABORTED";
          case -0x7ffb2fe6:
            return (int)"XACT_E_LOGFULL";
          case -0x7ffb2fe5:
            return (int)"XACT_E_TMNOTAVAILABLE";
          case -0x7ffb2fe4:
            return (int)"XACT_E_CONNECTION_DOWN";
          case -0x7ffb2fe3:
            return (int)"XACT_E_CONNECTION_DENIED";
          case -0x7ffb2fe2:
            return (int)"XACT_E_REENLISTTIMEOUT";
          case -0x7ffb2fe1:
            return (int)"XACT_E_TIP_CONNECT_FAILED";
          case -0x7ffb2fe0:
            return (int)"XACT_E_TIP_PROTOCOL_ERROR";
          case -0x7ffb2fdf:
            return (int)"XACT_E_TIP_PULL_FAILED";
          case -0x7ffb2fde:
            return (int)"XACT_E_DEST_TMNOTAVAILABLE";
          case -0x7ffb2fdd:
            return (int)"XACT_E_TIP_DISABLED";
          case -0x7ffb2fdc:
            return (int)"XACT_E_NETWORK_TX_DISABLED";
          case -0x7ffb2fdb:
            return (int)"XACT_E_PARTNER_NETWORK_TX_DISABLED";
          case -0x7ffb2fda:
            return (int)"XACT_E_XA_TX_DISABLED";
          case -0x7ffb2fd9:
            return (int)"XACT_E_UNABLE_TO_READ_DTC_CONFIG";
          case -0x7ffb2fd8:
            return (int)"XACT_E_UNABLE_TO_LOAD_DTC_PROXY";
          case -0x7ffb2fd7:
            return (int)"XACT_E_LAST";
          }
        }
        else if (in_stack_00000004 < -0x7ff8ffdb) {
          if (in_stack_00000004 == -0x7ff8ffdc) goto switchD_005c46de_caseD_24;
          if (in_stack_00000004 < -0x7ff8fffc) {
            if (in_stack_00000004 == -0x7ff8fffd) {
LAB_005c46a0:
              return (int)"ERROR_PATH_NOT_FOUND";
            }
            if (in_stack_00000004 < -0x7ffb1fdd) {
              if (in_stack_00000004 == -0x7ffb1fde) {
                return (int)"CO_E_ACTIVATIONFAILED_EVENTLOGGED";
              }
              if (in_stack_00000004 < -0x7ffb1ffc) {
                if (in_stack_00000004 == -0x7ffb1ffd) {
                  return (int)"CONTEXT_E_ABORTING";
                }
                if (in_stack_00000004 == -0x7ffb2f7f) {
                  return (int)"XACT_E_CLERKEXISTS";
                }
                if (in_stack_00000004 == -0x7ffb2f7e) {
                  return (int)"XACT_E_RECOVERYINPROGRESS";
                }
                if (in_stack_00000004 == -0x7ffb2f7d) {
                  return (int)"XACT_E_TRANSACTIONCLOSED";
                }
                if (in_stack_00000004 == -0x7ffb2f7c) {
                  return (int)"XACT_E_INVALIDLSN";
                }
                if (in_stack_00000004 == -0x7ffb2f7b) {
                  return (int)"XACT_E_REPLAYREQUEST";
                }
                if (in_stack_00000004 == -0x7ffb2000) {
                  return (int)"CONTEXT_E_FIRST";
                }
                if (in_stack_00000004 == -0x7ffb1ffe) {
                  return (int)"CONTEXT_E_ABORTED";
                }
              }
              else {
                if (in_stack_00000004 == -0x7ffb1ffc) {
                  return (int)"CONTEXT_E_NOCONTEXT";
                }
                if (in_stack_00000004 == -0x7ffb1ffb) {
                  return (int)"CONTEXT_E_WOULD_DEADLOCK";
                }
                if (in_stack_00000004 == -0x7ffb1ffa) {
                  return (int)"CONTEXT_E_SYNCH_TIMEOUT";
                }
                if (in_stack_00000004 == -0x7ffb1ff9) {
                  return (int)"CONTEXT_E_OLDREF";
                }
                if (in_stack_00000004 == -0x7ffb1ff4) {
                  return (int)"CONTEXT_E_ROLENOTFOUND";
                }
                if (in_stack_00000004 == -0x7ffb1ff1) {
                  return (int)"CONTEXT_E_TMNOTAVAILABLE";
                }
                if (in_stack_00000004 == -0x7ffb1fdf) {
                  return (int)"CO_E_ACTIVATIONFAILED";
                }
              }
            }
            else if (in_stack_00000004 < -0x7ff8fffe) {
              if (in_stack_00000004 == -0x7ff8ffff) {
                return (int)"ERROR_INVALID_FUNCTION";
              }
              switch(in_stack_00000004) {
              case -0x7ffb1fdd:
                return (int)"CO_E_ACTIVATIONFAILED_CATALOGERROR";
              case -0x7ffb1fdc:
                return (int)"CO_E_ACTIVATIONFAILED_TIMEOUT";
              case -0x7ffb1fdb:
                return (int)"CO_E_INITIALIZATIONFAILED";
              case -0x7ffb1fda:
                return (int)"CONTEXT_E_NOJIT";
              case -0x7ffb1fd9:
                return (int)"CONTEXT_E_NOTRANSACTION";
              case -0x7ffb1fd8:
                return (int)"CO_E_THREADINGMODEL_CHANGED";
              case -0x7ffb1fd7:
                return (int)"CO_E_NOIISINTRINSICS";
              case -0x7ffb1fd6:
                return (int)"CO_E_NOCOOKIES";
              case -0x7ffb1fd5:
                return (int)"CO_E_DBERROR";
              case -0x7ffb1fd4:
                return (int)"CO_E_NOTPOOLED";
              case -0x7ffb1fd3:
                return (int)"CO_E_NOTCONSTRUCTED";
              case -0x7ffb1fd2:
                return (int)"CO_E_NOSYNCHRONIZATION";
              case -0x7ffb1fd1:
                return (int)"CONTEXT_E_LAST";
              }
            }
            else if (in_stack_00000004 == -0x7ff8fffe) goto LAB_005c042a;
          }
          else {
            switch(in_stack_00000004) {
            case -0x7ff8fffc:
switchD_005c0442_caseD_80070004:
              return (int)"ERROR_TOO_MANY_OPEN_FILES";
            case -0x7ff8fffb:
              return (int)"E_ACCESSDENIED";
            case -0x7ff8fffa:
              return (int)"E_HANDLE";
            case -0x7ff8fff9:
              goto switchD_005c0442_caseD_80070007;
            case -0x7ff8fff8:
              goto switchD_005c0442_caseD_80070008;
            case -0x7ff8fff7:
              goto switchD_005c0442_caseD_80070009;
            case -0x7ff8fff6:
              goto switchD_005c0442_caseD_8007000a;
            case -0x7ff8fff5:
              goto switchD_005c0442_caseD_8007000b;
            case -0x7ff8fff4:
              goto switchD_005c0442_caseD_8007000c;
            case -0x7ff8fff3:
              goto switchD_005c0442_caseD_8007000d;
            case -0x7ff8fff2:
              return (int)"E_OUTOFMEMORY";
            case -0x7ff8fff1:
              goto switchD_005c0442_caseD_8007000f;
            case -0x7ff8fff0:
              goto switchD_005c0442_caseD_80070010;
            case -0x7ff8ffef:
              goto switchD_005c0442_caseD_80070011;
            case -0x7ff8ffee:
              goto switchD_005c0442_caseD_80070012;
            case -0x7ff8ffed:
              goto switchD_005c0442_caseD_80070013;
            case -0x7ff8ffec:
              goto switchD_005c0442_caseD_80070014;
            case -0x7ff8ffeb:
              goto switchD_005c0442_caseD_80070015;
            case -0x7ff8ffea:
              goto switchD_005c0442_caseD_80070016;
            case -0x7ff8ffe9:
              goto switchD_005c0442_caseD_80070017;
            case -0x7ff8ffe8:
              goto switchD_005c0442_caseD_80070018;
            case -0x7ff8ffe7:
              goto switchD_005c0442_caseD_80070019;
            case -0x7ff8ffe6:
              goto switchD_005c0442_caseD_8007001a;
            case -0x7ff8ffe5:
              goto switchD_005c0442_caseD_8007001b;
            case -0x7ff8ffe4:
              goto switchD_005c0442_caseD_8007001c;
            case -0x7ff8ffe3:
              goto switchD_005c0442_caseD_8007001d;
            case -0x7ff8ffe2:
              goto switchD_005c0442_caseD_8007001e;
            case -0x7ff8ffe1:
              goto switchD_005c0442_caseD_8007001f;
            case -0x7ff8ffe0:
              goto switchD_005c0442_caseD_80070020;
            case -0x7ff8ffdf:
              goto switchD_005c0442_caseD_80070021;
            case -0x7ff8ffde:
              goto switchD_005c0442_caseD_80070022;
            }
          }
        }
        else {
          switch(in_stack_00000004) {
          case -0x7ff8ffda:
            goto switchD_005c047c_caseD_80070026;
          case -0x7ff8ffd9:
            goto switchD_005c047c_caseD_80070027;
          case -0x7ff8ffce:
            goto switchD_005c047c_caseD_80070032;
          case -0x7ff8ffcd:
            goto switchD_005c047c_caseD_80070033;
          case -0x7ff8ffcc:
            goto switchD_005c047c_caseD_80070034;
          case -0x7ff8ffcb:
            goto switchD_005c047c_caseD_80070035;
          case -0x7ff8ffca:
            goto switchD_005c047c_caseD_80070036;
          case -0x7ff8ffc9:
            goto switchD_005c047c_caseD_80070037;
          case -0x7ff8ffc8:
            goto switchD_005c047c_caseD_80070038;
          case -0x7ff8ffc7:
            goto switchD_005c047c_caseD_80070039;
          case -0x7ff8ffc6:
            goto switchD_005c047c_caseD_8007003a;
          case -0x7ff8ffc5:
            goto switchD_005c047c_caseD_8007003b;
          case -0x7ff8ffc4:
            goto switchD_005c047c_caseD_8007003c;
          case -0x7ff8ffc3:
            goto switchD_005c047c_caseD_8007003d;
          case -0x7ff8ffc2:
            goto switchD_005c047c_caseD_8007003e;
          case -0x7ff8ffc1:
            goto switchD_005c047c_caseD_8007003f;
          case -0x7ff8ffc0:
            goto switchD_005c047c_caseD_80070040;
          case -0x7ff8ffbf:
            goto switchD_005c047c_caseD_80070041;
          case -0x7ff8ffbe:
            goto switchD_005c047c_caseD_80070042;
          case -0x7ff8ffbd:
            goto switchD_005c047c_caseD_80070043;
          case -0x7ff8ffbc:
            goto switchD_005c047c_caseD_80070044;
          case -0x7ff8ffbb:
            goto switchD_005c047c_caseD_80070045;
          case -0x7ff8ffba:
            goto switchD_005c047c_caseD_80070046;
          case -0x7ff8ffb9:
            goto switchD_005c047c_caseD_80070047;
          case -0x7ff8ffb8:
            goto switchD_005c047c_caseD_80070048;
          case -0x7ff8ffb0:
            goto switchD_005c047c_caseD_80070050;
          case -0x7ff8ffae:
            goto switchD_005c047c_caseD_80070052;
          case -0x7ff8ffad:
            goto switchD_005c047c_caseD_80070053;
          case -0x7ff8ffac:
            goto switchD_005c047c_caseD_80070054;
          case -0x7ff8ffab:
            goto switchD_005c047c_caseD_80070055;
          case -0x7ff8ffaa:
            goto switchD_005c047c_caseD_80070056;
          case -0x7ff8ffa9:
            return (int)"E_INVALIDARG";
          case -0x7ff8ffa8:
            goto switchD_005c047c_caseD_80070058;
          case -0x7ff8ffa7:
            goto switchD_005c047c_caseD_80070059;
          case -0x7ff8ff9c:
            goto switchD_005c047c_caseD_80070064;
          case -0x7ff8ff9b:
            goto switchD_005c047c_caseD_80070065;
          case -0x7ff8ff9a:
            goto switchD_005c047c_caseD_80070066;
          case -0x7ff8ff99:
            goto switchD_005c047c_caseD_80070067;
          case -0x7ff8ff98:
            goto switchD_005c047c_caseD_80070068;
          case -0x7ff8ff97:
            goto switchD_005c047c_caseD_80070069;
          case -0x7ff8ff96:
            goto switchD_005c047c_caseD_8007006a;
          case -0x7ff8ff95:
            goto switchD_005c047c_caseD_8007006b;
          case -0x7ff8ff94:
            goto switchD_005c047c_caseD_8007006c;
          case -0x7ff8ff93:
            goto switchD_005c047c_caseD_8007006d;
          case -0x7ff8ff92:
            goto switchD_005c047c_caseD_8007006e;
          case -0x7ff8ff91:
            goto switchD_005c047c_caseD_8007006f;
          case -0x7ff8ff90:
            goto switchD_005c047c_caseD_80070070;
          case -0x7ff8ff8f:
            goto switchD_005c047c_caseD_80070071;
          case -0x7ff8ff8e:
            goto switchD_005c047c_caseD_80070072;
          case -0x7ff8ff8b:
            goto switchD_005c047c_caseD_80070075;
          case -0x7ff8ff8a:
            goto switchD_005c047c_caseD_80070076;
          case -0x7ff8ff89:
            goto switchD_005c047c_caseD_80070077;
          case -0x7ff8ff88:
            goto switchD_005c047c_caseD_80070078;
          case -0x7ff8ff87:
            goto switchD_005c047c_caseD_80070079;
          case -0x7ff8ff86:
            goto switchD_005c047c_caseD_8007007a;
          case -0x7ff8ff85:
            goto switchD_005c047c_caseD_8007007b;
          case -0x7ff8ff84:
            goto switchD_005c047c_caseD_8007007c;
          case -0x7ff8ff83:
            goto switchD_005c047c_caseD_8007007d;
          case -0x7ff8ff82:
            goto switchD_005c047c_caseD_8007007e;
          case -0x7ff8ff81:
            goto switchD_005c047c_caseD_8007007f;
          case -0x7ff8ff80:
            goto switchD_005c047c_caseD_80070080;
          case -0x7ff8ff7f:
            goto switchD_005c047c_caseD_80070081;
          }
        }
      }
      else if (in_stack_00000004 < -0x7ff8ff0f) {
        if (in_stack_00000004 == -0x7ff8ff10) {
switchD_005c4de8_caseD_f0:
          return (int)"ERROR_VC_DISCONNECTED";
        }
        switch(in_stack_00000004) {
        case -0x7ff8ff7d:
switchD_005c04b1_caseD_80070083:
          return (int)"ERROR_NEGATIVE_SEEK";
        case -0x7ff8ff7c:
switchD_005c04b1_caseD_80070084:
          return (int)"ERROR_SEEK_ON_DEVICE";
        case -0x7ff8ff7b:
switchD_005c04b1_caseD_80070085:
          return (int)"ERROR_IS_JOIN_TARGET";
        case -0x7ff8ff7a:
switchD_005c04b1_caseD_80070086:
          return (int)"ERROR_IS_JOINED";
        case -0x7ff8ff79:
switchD_005c04b1_caseD_80070087:
          return (int)"ERROR_IS_SUBSTED";
        case -0x7ff8ff78:
switchD_005c04b1_caseD_80070088:
          return (int)"ERROR_NOT_JOINED";
        case -0x7ff8ff77:
switchD_005c04b1_caseD_80070089:
          return (int)"ERROR_NOT_SUBSTED";
        case -0x7ff8ff76:
switchD_005c04b1_caseD_8007008a:
          return (int)"ERROR_JOIN_TO_JOIN";
        case -0x7ff8ff75:
switchD_005c04b1_caseD_8007008b:
          return (int)"ERROR_SUBST_TO_SUBST";
        case -0x7ff8ff74:
switchD_005c04b1_caseD_8007008c:
          return (int)"ERROR_JOIN_TO_SUBST";
        case -0x7ff8ff73:
switchD_005c04b1_caseD_8007008d:
          return (int)"ERROR_SUBST_TO_JOIN";
        case -0x7ff8ff72:
switchD_005c04b1_caseD_8007008e:
          return (int)"ERROR_BUSY_DRIVE";
        case -0x7ff8ff71:
switchD_005c04b1_caseD_8007008f:
          return (int)"ERROR_SAME_DRIVE";
        case -0x7ff8ff70:
switchD_005c04b1_caseD_80070090:
          return (int)"ERROR_DIR_NOT_ROOT";
        case -0x7ff8ff6f:
switchD_005c04b1_caseD_80070091:
          return (int)"ERROR_DIR_NOT_EMPTY";
        case -0x7ff8ff6e:
switchD_005c04b1_caseD_80070092:
          return (int)"ERROR_IS_SUBST_PATH";
        case -0x7ff8ff6d:
switchD_005c04b1_caseD_80070093:
          return (int)"ERROR_IS_JOIN_PATH";
        case -0x7ff8ff6c:
switchD_005c04b1_caseD_80070094:
          return (int)"ERROR_PATH_BUSY";
        case -0x7ff8ff6b:
switchD_005c04b1_caseD_80070095:
          return (int)"ERROR_IS_SUBST_TARGET";
        case -0x7ff8ff6a:
switchD_005c04b1_caseD_80070096:
          return (int)"ERROR_SYSTEM_TRACE";
        case -0x7ff8ff69:
switchD_005c04b1_caseD_80070097:
          return (int)"ERROR_INVALID_EVENT_COUNT";
        case -0x7ff8ff68:
switchD_005c04b1_caseD_80070098:
          return (int)"ERROR_TOO_MANY_MUXWAITERS";
        case -0x7ff8ff67:
switchD_005c04b1_caseD_80070099:
          return (int)"ERROR_INVALID_LIST_FORMAT";
        case -0x7ff8ff66:
switchD_005c04b1_caseD_8007009a:
          return (int)"ERROR_LABEL_TOO_LONG";
        case -0x7ff8ff65:
switchD_005c04b1_caseD_8007009b:
          return (int)"ERROR_TOO_MANY_TCBS";
        case -0x7ff8ff64:
switchD_005c04b1_caseD_8007009c:
          return (int)"ERROR_SIGNAL_REFUSED";
        case -0x7ff8ff63:
switchD_005c04b1_caseD_8007009d:
          return (int)"ERROR_DISCARDED";
        case -0x7ff8ff62:
switchD_005c04b1_caseD_8007009e:
          return (int)"ERROR_NOT_LOCKED";
        case -0x7ff8ff61:
switchD_005c04b1_caseD_8007009f:
          return (int)"ERROR_BAD_THREADID_ADDR";
        case -0x7ff8ff60:
switchD_005c04b1_caseD_800700a0:
          return (int)"ERROR_BAD_ARGUMENTS";
        case -0x7ff8ff5f:
switchD_005c04b1_caseD_800700a1:
          return (int)"ERROR_BAD_PATHNAME";
        case -0x7ff8ff5e:
switchD_005c04b1_caseD_800700a2:
          return (int)"ERROR_SIGNAL_PENDING";
        case -0x7ff8ff5c:
switchD_005c04b1_caseD_800700a4:
          return (int)"ERROR_MAX_THRDS_REACHED";
        case -0x7ff8ff59:
switchD_005c04b1_caseD_800700a7:
          return (int)"ERROR_LOCK_FAILED";
        case -0x7ff8ff56:
switchD_005c04b1_caseD_800700aa:
          return (int)"ERROR_BUSY & DIERR_ACQUIRED";
        case -0x7ff8ff53:
switchD_005c04b1_caseD_800700ad:
          return (int)"ERROR_CANCEL_VIOLATION";
        case -0x7ff8ff52:
switchD_005c04b1_caseD_800700ae:
          return (int)"ERROR_ATOMIC_LOCKS_NOT_SUPPORTED";
        case -0x7ff8ff4c:
switchD_005c04b1_caseD_800700b4:
          return (int)"ERROR_INVALID_SEGMENT_NUMBER";
        case -0x7ff8ff4a:
switchD_005c04b1_caseD_800700b6:
          return (int)"ERROR_INVALID_ORDINAL";
        case -0x7ff8ff49:
switchD_005c04b1_caseD_800700b7:
          return (int)"ERROR_ALREADY_EXISTS";
        case -0x7ff8ff46:
switchD_005c04b1_caseD_800700ba:
          return (int)"ERROR_INVALID_FLAG_NUMBER";
        case -0x7ff8ff45:
switchD_005c04b1_caseD_800700bb:
          return (int)"ERROR_SEM_NOT_FOUND";
        case -0x7ff8ff44:
switchD_005c04b1_caseD_800700bc:
          return (int)"ERROR_INVALID_STARTING_CODESEG";
        case -0x7ff8ff43:
switchD_005c04b1_caseD_800700bd:
          return (int)"ERROR_INVALID_STACKSEG";
        case -0x7ff8ff42:
switchD_005c04b1_caseD_800700be:
          return (int)"ERROR_INVALID_MODULETYPE";
        case -0x7ff8ff41:
switchD_005c04b1_caseD_800700bf:
          return (int)"ERROR_INVALID_EXE_SIGNATURE";
        case -0x7ff8ff40:
switchD_005c04b1_caseD_800700c0:
          return (int)"ERROR_EXE_MARKED_INVALID";
        case -0x7ff8ff3f:
switchD_005c04b1_caseD_800700c1:
          return (int)"ERROR_BAD_EXE_FORMAT";
        case -0x7ff8ff3e:
switchD_005c04b1_caseD_800700c2:
          return (int)"ERROR_ITERATED_DATA_EXCEEDS_64k";
        case -0x7ff8ff3d:
switchD_005c04b1_caseD_800700c3:
          return (int)"ERROR_INVALID_MINALLOCSIZE";
        case -0x7ff8ff3c:
switchD_005c04b1_caseD_800700c4:
          return (int)"ERROR_DYNLINK_FROM_INVALID_RING";
        case -0x7ff8ff3b:
switchD_005c04b1_caseD_800700c5:
          return (int)"ERROR_IOPL_NOT_ENABLED";
        case -0x7ff8ff3a:
switchD_005c04b1_caseD_800700c6:
          return (int)"ERROR_INVALID_SEGDPL";
        case -0x7ff8ff39:
switchD_005c04b1_caseD_800700c7:
          return (int)"ERROR_AUTODATASEG_EXCEEDS_64k";
        case -0x7ff8ff36:
switchD_005c04b1_caseD_800700ca:
          return (int)"ERROR_INFLOOP_IN_RELOC_CHAIN";
        case -0x7ff8ff35:
switchD_005c04b1_caseD_800700cb:
          return (int)"ERROR_ENVVAR_NOT_FOUND";
        case -0x7ff8ff33:
switchD_005c04b1_caseD_800700cd:
          return (int)"ERROR_NO_SIGNAL_SENT";
        case -0x7ff8ff32:
switchD_005c04b1_caseD_800700ce:
          return (int)"ERROR_FILENAME_EXCED_RANGE";
        case -0x7ff8ff31:
switchD_005c04b1_caseD_800700cf:
          return (int)"ERROR_RING2_STACK_IN_USE";
        case -0x7ff8ff30:
switchD_005c04b1_caseD_800700d0:
          return (int)"ERROR_META_EXPANSION_TOO_LONG";
        case -0x7ff8ff2f:
switchD_005c04b1_caseD_800700d1:
          return (int)"ERROR_INVALID_SIGNAL_NUMBER";
        case -0x7ff8ff2e:
switchD_005c04b1_caseD_800700d2:
          return (int)"ERROR_THREAD_1_INACTIVE";
        case -0x7ff8ff2c:
switchD_005c04b1_caseD_800700d4:
          return (int)"ERROR_LOCKED";
        case -0x7ff8ff2a:
switchD_005c04b1_caseD_800700d6:
          return (int)"ERROR_TOO_MANY_MODULES";
        case -0x7ff8ff29:
switchD_005c04b1_caseD_800700d7:
          return (int)"ERROR_NESTING_NOT_ALLOWED";
        case -0x7ff8ff28:
switchD_005c04b1_caseD_800700d8:
          return (int)"ERROR_EXE_MACHINE_TYPE_MISMATCH";
        case -0x7ff8ff27:
switchD_005c04b1_caseD_800700d9:
          return (int)"ERROR_EXE_CANNOT_MODIFY_SIGNED_BINARY";
        case -0x7ff8ff26:
switchD_005c04b1_caseD_800700da:
          return (int)"ERROR_EXE_CANNOT_MODIFY_STRONG_SIGNED_BINARY";
        case -0x7ff8ff1a:
switchD_005c04b1_caseD_800700e6:
          return (int)"ERROR_BAD_PIPE";
        case -0x7ff8ff19:
switchD_005c04b1_caseD_800700e7:
          return (int)"ERROR_PIPE_BUSY";
        case -0x7ff8ff18:
switchD_005c04b1_caseD_800700e8:
          return (int)"ERROR_NO_DATA";
        case -0x7ff8ff17:
switchD_005c04b1_caseD_800700e9:
          return (int)"ERROR_PIPE_NOT_CONNECTED";
        case -0x7ff8ff16:
switchD_005c04b1_caseD_800700ea:
          return (int)"ERROR_MORE_DATA";
        }
      }
      else if (in_stack_00000004 < -0x7ff8faac) {
        if (in_stack_00000004 == -0x7ff8faad) goto switchD_005c5350_caseD_553;
        if (in_stack_00000004 < -0x7ff8fb67) {
          if (in_stack_00000004 == -0x7ff8fb68) goto switchD_005c5350_caseD_498;
          if (in_stack_00000004 < -0x7ff8fbcf) {
            if (in_stack_00000004 == -0x7ff8fbd0) goto switchD_005c4ffb_caseD_430;
            if (in_stack_00000004 < -0x7ff8fc10) {
              if (in_stack_00000004 == -0x7ff8fc11) goto switchD_005c4f79_caseD_3ef;
              if (in_stack_00000004 < -0x7ff8fec2) {
                if (in_stack_00000004 == -0x7ff8fec3) goto LAB_005c4eb7;
                switch(in_stack_00000004) {
                case -0x7ff8ff02:
                  goto switchD_005c0526_caseD_800700fe;
                case -0x7ff8ff01:
                  goto switchD_005c0526_caseD_800700ff;
                case -0x7ff8fefe:
                  goto switchD_005c0526_caseD_80070102;
                case -0x7ff8fefd:
                  goto switchD_005c0526_caseD_80070103;
                case -0x7ff8fef6:
                  goto switchD_005c0526_caseD_8007010a;
                case -0x7ff8fef5:
                  goto switchD_005c0526_caseD_8007010b;
                case -0x7ff8feed:
                  goto switchD_005c0526_caseD_80070113;
                case -0x7ff8feec:
                  goto switchD_005c0526_caseD_80070114;
                case -0x7ff8feeb:
                  goto switchD_005c0526_caseD_80070115;
                case -0x7ff8feea:
                  goto switchD_005c0526_caseD_80070116;
                case -0x7ff8fee6:
                  goto switchD_005c0526_caseD_8007011a;
                case -0x7ff8fee0:
                  goto switchD_005c0526_caseD_80070120;
                case -0x7ff8fed6:
                  goto switchD_005c0526_caseD_8007012a;
                case -0x7ff8fed5:
                  goto switchD_005c0526_caseD_8007012b;
                case -0x7ff8fed4:
                  goto switchD_005c0526_caseD_8007012c;
                case -0x7ff8fed3:
                  goto switchD_005c0526_caseD_8007012d;
                case -0x7ff8fed2:
                  goto switchD_005c0526_caseD_8007012e;
                case -0x7ff8fed1:
                  goto switchD_005c0526_caseD_8007012f;
                }
              }
              else if (in_stack_00000004 < -0x7ff8fc1a) {
                if (in_stack_00000004 == -0x7ff8fc1b) {
LAB_005c4f43:
                  return (int)"ERROR_IO_PENDING";
                }
                if (in_stack_00000004 < -0x7ff8fde7) {
                  if (in_stack_00000004 == -0x7ff8fde8) goto LAB_005c4f21;
                  if (in_stack_00000004 == -0x7ff8fec2) goto LAB_005c4f17;
                  if (in_stack_00000004 == -0x7ff8fe19) goto LAB_005c4f0d;
                  if (in_stack_00000004 == -0x7ff8fdea) goto LAB_005c4f03;
                  if (in_stack_00000004 == -0x7ff8fde9) goto LAB_005c4ef9;
                }
                else {
                  if (in_stack_00000004 == -0x7ff8fc1e) goto LAB_005c4f57;
                  if (in_stack_00000004 == -0x7ff8fc1d) goto LAB_005c4f4d;
                  if (in_stack_00000004 == -0x7ff8fc1c) goto LAB_005c059d;
                }
              }
              else {
                switch(in_stack_00000004) {
                case -0x7ff8fc1a:
                  goto switchD_005c05b5_caseD_800703e6;
                case -0x7ff8fc19:
                  goto switchD_005c05b5_caseD_800703e7;
                case -0x7ff8fc17:
                  goto switchD_005c05b5_caseD_800703e9;
                case -0x7ff8fc16:
                  goto switchD_005c05b5_caseD_800703ea;
                case -0x7ff8fc15:
                  goto switchD_005c05b5_caseD_800703eb;
                case -0x7ff8fc14:
                  goto switchD_005c05b5_caseD_800703ec;
                case -0x7ff8fc13:
                  goto switchD_005c05b5_caseD_800703ed;
                case -0x7ff8fc12:
                  goto switchD_005c05b5_caseD_800703ee;
                }
              }
            }
            else {
              switch(in_stack_00000004) {
              case -0x7ff8fc10:
                goto switchD_005c05d1_caseD_800703f0;
              case -0x7ff8fc0f:
                goto switchD_005c05d1_caseD_800703f1;
              case -0x7ff8fc0e:
                goto switchD_005c05d1_caseD_800703f2;
              case -0x7ff8fc0d:
                goto switchD_005c05d1_caseD_800703f3;
              case -0x7ff8fc0c:
                goto switchD_005c05d1_caseD_800703f4;
              case -0x7ff8fc0b:
                goto switchD_005c05d1_caseD_800703f5;
              case -0x7ff8fc0a:
                goto switchD_005c05d1_caseD_800703f6;
              case -0x7ff8fc09:
                goto switchD_005c05d1_caseD_800703f7;
              case -0x7ff8fc08:
                goto switchD_005c05d1_caseD_800703f8;
              case -0x7ff8fc07:
                goto switchD_005c05d1_caseD_800703f9;
              case -0x7ff8fc06:
                goto switchD_005c05d1_caseD_800703fa;
              case -0x7ff8fc05:
                goto switchD_005c05d1_caseD_800703fb;
              case -0x7ff8fc04:
                goto switchD_005c05d1_caseD_800703fc;
              case -0x7ff8fc03:
                goto switchD_005c05d1_caseD_800703fd;
              case -0x7ff8fc02:
                goto switchD_005c05d1_caseD_800703fe;
              case -0x7ff8fbe5:
                goto switchD_005c05d1_caseD_8007041b;
              case -0x7ff8fbe4:
                goto switchD_005c05d1_caseD_8007041c;
              case -0x7ff8fbe3:
                goto switchD_005c05d1_caseD_8007041d;
              case -0x7ff8fbe2:
                goto switchD_005c05d1_caseD_8007041e;
              case -0x7ff8fbe1:
                goto switchD_005c05d1_caseD_8007041f;
              case -0x7ff8fbe0:
                goto switchD_005c05d1_caseD_80070420;
              case -0x7ff8fbdf:
                goto switchD_005c05d1_caseD_80070421;
              case -0x7ff8fbde:
                goto switchD_005c05d1_caseD_80070422;
              case -0x7ff8fbdd:
                goto switchD_005c05d1_caseD_80070423;
              case -0x7ff8fbdc:
                goto switchD_005c05d1_caseD_80070424;
              case -0x7ff8fbdb:
                goto switchD_005c05d1_caseD_80070425;
              case -0x7ff8fbda:
                goto switchD_005c05d1_caseD_80070426;
              case -0x7ff8fbd9:
                goto switchD_005c05d1_caseD_80070427;
              case -0x7ff8fbd8:
                goto switchD_005c05d1_caseD_80070428;
              case -0x7ff8fbd7:
                goto switchD_005c05d1_caseD_80070429;
              case -0x7ff8fbd6:
                goto switchD_005c05d1_caseD_8007042a;
              case -0x7ff8fbd5:
                goto switchD_005c05d1_caseD_8007042b;
              case -0x7ff8fbd4:
                goto switchD_005c05d1_caseD_8007042c;
              case -0x7ff8fbd3:
                goto switchD_005c05d1_caseD_8007042d;
              case -0x7ff8fbd2:
                goto switchD_005c05d1_caseD_8007042e;
              case -0x7ff8fbd1:
                goto switchD_005c05d1_caseD_8007042f;
              }
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7ff8fbcf:
              goto switchD_005c05ed_caseD_80070431;
            case -0x7ff8fbce:
              goto switchD_005c05ed_caseD_80070432;
            case -0x7ff8fbcd:
              goto switchD_005c05ed_caseD_80070433;
            case -0x7ff8fbcc:
              goto switchD_005c05ed_caseD_80070434;
            case -0x7ff8fbcb:
              goto switchD_005c05ed_caseD_80070435;
            case -0x7ff8fbca:
              goto switchD_005c05ed_caseD_80070436;
            case -0x7ff8fbc9:
              goto switchD_005c05ed_caseD_80070437;
            case -0x7ff8fbc8:
              goto switchD_005c05ed_caseD_80070438;
            case -0x7ff8fbc7:
              goto switchD_005c05ed_caseD_80070439;
            case -0x7ff8fbc6:
              goto switchD_005c05ed_caseD_8007043a;
            case -0x7ff8fbc5:
              goto switchD_005c05ed_caseD_8007043b;
            case -0x7ff8fbc4:
              goto switchD_005c05ed_caseD_8007043c;
            case -0x7ff8fbb4:
              goto switchD_005c05ed_caseD_8007044c;
            case -0x7ff8fbb3:
              goto switchD_005c05ed_caseD_8007044d;
            case -0x7ff8fbb2:
              goto switchD_005c05ed_caseD_8007044e;
            case -0x7ff8fbb1:
              goto switchD_005c05ed_caseD_8007044f;
            case -0x7ff8fbb0:
              goto switchD_005c05ed_caseD_80070450;
            case -0x7ff8fbaf:
              goto switchD_005c05ed_caseD_80070451;
            case -0x7ff8fbae:
              goto switchD_005c05ed_caseD_80070452;
            case -0x7ff8fbad:
              goto switchD_005c05ed_caseD_80070453;
            case -0x7ff8fbac:
              goto switchD_005c05ed_caseD_80070454;
            case -0x7ff8fbab:
              goto switchD_005c05ed_caseD_80070455;
            case -0x7ff8fbaa:
              goto switchD_005c05ed_caseD_80070456;
            case -0x7ff8fba9:
              goto switchD_005c05ed_caseD_80070457;
            case -0x7ff8fba8:
              goto switchD_005c05ed_caseD_80070458;
            case -0x7ff8fba7:
              goto switchD_005c05ed_caseD_80070459;
            case -0x7ff8fba6:
              goto switchD_005c05ed_caseD_8007045a;
            case -0x7ff8fba5:
              goto switchD_005c05ed_caseD_8007045b;
            case -0x7ff8fba4:
              goto switchD_005c05ed_caseD_8007045c;
            case -0x7ff8fba3:
              goto switchD_005c05ed_caseD_8007045d;
            case -0x7ff8fba2:
              goto switchD_005c05ed_caseD_8007045e;
            case -0x7ff8fba1:
              goto switchD_005c05ed_caseD_8007045f;
            case -0x7ff8fba0:
              goto switchD_005c05ed_caseD_80070460;
            case -0x7ff8fb9f:
              goto switchD_005c05ed_caseD_80070461;
            case -0x7ff8fb9e:
              goto switchD_005c05ed_caseD_80070462;
            case -0x7ff8fb9d:
              goto switchD_005c05ed_caseD_80070463;
            case -0x7ff8fb9c:
              goto switchD_005c05ed_caseD_80070464;
            case -0x7ff8fb9b:
              goto switchD_005c05ed_caseD_80070465;
            case -0x7ff8fb9a:
              goto switchD_005c05ed_caseD_80070466;
            case -0x7ff8fb99:
              goto switchD_005c05ed_caseD_80070467;
            case -0x7ff8fb98:
              goto switchD_005c05ed_caseD_80070468;
            case -0x7ff8fb97:
              goto switchD_005c05ed_caseD_80070469;
            case -0x7ff8fb96:
              goto switchD_005c05ed_caseD_8007046a;
            case -0x7ff8fb95:
              goto switchD_005c05ed_caseD_8007046b;
            case -0x7ff8fb94:
              goto switchD_005c05ed_caseD_8007046c;
            case -0x7ff8fb8c:
              goto switchD_005c05ed_caseD_80070474;
            case -0x7ff8fb8b:
              goto switchD_005c05ed_caseD_80070475;
            case -0x7ff8fb8a:
              goto switchD_005c05ed_caseD_80070476;
            case -0x7ff8fb82:
              goto switchD_005c05ed_caseD_8007047e;
            case -0x7ff8fb81:
              goto switchD_005c05ed_caseD_8007047f;
            case -0x7ff8fb80:
              goto switchD_005c05ed_caseD_80070480;
            case -0x7ff8fb7f:
              goto switchD_005c05ed_caseD_80070481;
            case -0x7ff8fb7e:
              goto switchD_005c05ed_caseD_80070482;
            case -0x7ff8fb7d:
              goto switchD_005c05ed_caseD_80070483;
            case -0x7ff8fb7c:
              goto switchD_005c05ed_caseD_80070484;
            case -0x7ff8fb7b:
              goto switchD_005c05ed_caseD_80070485;
            case -0x7ff8fb7a:
              goto switchD_005c05ed_caseD_80070486;
            case -0x7ff8fb79:
              goto switchD_005c05ed_caseD_80070487;
            case -0x7ff8fb78:
              goto switchD_005c05ed_caseD_80070488;
            case -0x7ff8fb77:
              goto switchD_005c05ed_caseD_80070489;
            case -0x7ff8fb76:
              goto switchD_005c05ed_caseD_8007048a;
            case -0x7ff8fb75:
              goto switchD_005c05ed_caseD_8007048b;
            case -0x7ff8fb74:
              goto switchD_005c05ed_caseD_8007048c;
            case -0x7ff8fb73:
              goto switchD_005c05ed_caseD_8007048d;
            case -0x7ff8fb72:
              goto switchD_005c05ed_caseD_8007048e;
            case -0x7ff8fb71:
              goto switchD_005c05ed_caseD_8007048f;
            case -0x7ff8fb70:
              goto switchD_005c05ed_caseD_80070490;
            case -0x7ff8fb6f:
              goto switchD_005c05ed_caseD_80070491;
            case -0x7ff8fb6e:
              goto switchD_005c05ed_caseD_80070492;
            case -0x7ff8fb6d:
              goto switchD_005c05ed_caseD_80070493;
            case -0x7ff8fb6c:
              goto switchD_005c05ed_caseD_80070494;
            case -0x7ff8fb6b:
              goto switchD_005c05ed_caseD_80070495;
            case -0x7ff8fb69:
              goto switchD_005c05ed_caseD_80070497;
            }
          }
        }
        else {
          switch(in_stack_00000004) {
          case -0x7ff8fb67:
            goto switchD_005c0604_caseD_80070499;
          case -0x7ff8fb66:
            goto switchD_005c0604_caseD_8007049a;
          case -0x7ff8fb65:
            goto switchD_005c0604_caseD_8007049b;
          case -0x7ff8fb64:
            goto switchD_005c0604_caseD_8007049c;
          case -0x7ff8fb63:
            goto switchD_005c0604_caseD_8007049d;
          case -0x7ff8fb50:
            goto switchD_005c0604_caseD_800704b0;
          case -0x7ff8fb4f:
            goto switchD_005c0604_caseD_800704b1;
          case -0x7ff8fb4e:
            goto switchD_005c0604_caseD_800704b2;
          case -0x7ff8fb4d:
            goto switchD_005c0604_caseD_800704b3;
          case -0x7ff8fb4c:
            goto switchD_005c0604_caseD_800704b4;
          case -0x7ff8fb4b:
            goto switchD_005c0604_caseD_800704b5;
          case -0x7ff8fb4a:
            goto switchD_005c0604_caseD_800704b6;
          case -0x7ff8fb49:
            goto switchD_005c0604_caseD_800704b7;
          case -0x7ff8fb48:
            goto switchD_005c0604_caseD_800704b8;
          case -0x7ff8fb47:
            goto switchD_005c0604_caseD_800704b9;
          case -0x7ff8fb46:
            goto switchD_005c0604_caseD_800704ba;
          case -0x7ff8fb45:
            goto switchD_005c0604_caseD_800704bb;
          case -0x7ff8fb44:
            goto switchD_005c0604_caseD_800704bc;
          case -0x7ff8fb43:
            goto switchD_005c0604_caseD_800704bd;
          case -0x7ff8fb42:
            goto switchD_005c0604_caseD_800704be;
          case -0x7ff8fb41:
            goto switchD_005c0604_caseD_800704bf;
          case -0x7ff8fb40:
            goto switchD_005c0604_caseD_800704c0;
          case -0x7ff8fb3f:
            goto switchD_005c0604_caseD_800704c1;
          case -0x7ff8fb3e:
            goto switchD_005c0604_caseD_800704c2;
          case -0x7ff8fb3d:
            goto switchD_005c0604_caseD_800704c3;
          case -0x7ff8fb3c:
            goto switchD_005c0604_caseD_800704c4;
          case -0x7ff8fb3b:
            goto switchD_005c0604_caseD_800704c5;
          case -0x7ff8fb3a:
            goto switchD_005c0604_caseD_800704c6;
          case -0x7ff8fb39:
            goto switchD_005c0604_caseD_800704c7;
          case -0x7ff8fb38:
            goto switchD_005c0604_caseD_800704c8;
          case -0x7ff8fb37:
            goto switchD_005c0604_caseD_800704c9;
          case -0x7ff8fb36:
            goto switchD_005c0604_caseD_800704ca;
          case -0x7ff8fb35:
            goto switchD_005c0604_caseD_800704cb;
          case -0x7ff8fb34:
            goto switchD_005c0604_caseD_800704cc;
          case -0x7ff8fb33:
            goto switchD_005c0604_caseD_800704cd;
          case -0x7ff8fb32:
            goto switchD_005c0604_caseD_800704ce;
          case -0x7ff8fb31:
            goto switchD_005c0604_caseD_800704cf;
          case -0x7ff8fb30:
            goto switchD_005c0604_caseD_800704d0;
          case -0x7ff8fb2f:
            goto switchD_005c0604_caseD_800704d1;
          case -0x7ff8fb2e:
            goto switchD_005c0604_caseD_800704d2;
          case -0x7ff8fb2d:
            goto switchD_005c0604_caseD_800704d3;
          case -0x7ff8fb2c:
            goto switchD_005c0604_caseD_800704d4;
          case -0x7ff8fb2b:
            goto switchD_005c0604_caseD_800704d5;
          case -0x7ff8fb2a:
            goto switchD_005c0604_caseD_800704d6;
          case -0x7ff8fb29:
            goto switchD_005c0604_caseD_800704d7;
          case -0x7ff8fb28:
            goto switchD_005c0604_caseD_800704d8;
          case -0x7ff8fb27:
            goto switchD_005c0604_caseD_800704d9;
          case -0x7ff8fb26:
            goto switchD_005c0604_caseD_800704da;
          case -0x7ff8fb25:
            goto switchD_005c0604_caseD_800704db;
          case -0x7ff8fb24:
            goto switchD_005c0604_caseD_800704dc;
          case -0x7ff8fb23:
            goto switchD_005c0604_caseD_800704dd;
          case -0x7ff8fb22:
            goto switchD_005c0604_caseD_800704de;
          case -0x7ff8fb21:
            goto switchD_005c0604_caseD_800704df;
          case -0x7ff8fb20:
            goto switchD_005c0604_caseD_800704e0;
          case -0x7ff8fb1f:
            goto switchD_005c0604_caseD_800704e1;
          case -0x7ff8fb1e:
            goto switchD_005c0604_caseD_800704e2;
          case -0x7ff8fb1d:
            goto switchD_005c0604_caseD_800704e3;
          case -0x7ff8fb1c:
            goto switchD_005c0604_caseD_800704e4;
          case -0x7ff8fb1b:
            goto switchD_005c0604_caseD_800704e5;
          case -0x7ff8fb1a:
            goto switchD_005c0604_caseD_800704e6;
          case -0x7ff8fb19:
            goto switchD_005c0604_caseD_800704e7;
          case -0x7ff8fb18:
            goto switchD_005c0604_caseD_800704e8;
          case -0x7ff8fb17:
            goto switchD_005c0604_caseD_800704e9;
          case -0x7ff8fb16:
            goto switchD_005c0604_caseD_800704ea;
          case -0x7ff8fb15:
            goto switchD_005c0604_caseD_800704eb;
          case -0x7ff8fb14:
            goto switchD_005c0604_caseD_800704ec;
          case -0x7ff8fb13:
            goto switchD_005c0604_caseD_800704ed;
          case -0x7ff8fb12:
            goto switchD_005c0604_caseD_800704ee;
          case -0x7ff8fb11:
            goto switchD_005c0604_caseD_800704ef;
          case -0x7ff8fb10:
            goto switchD_005c0604_caseD_800704f0;
          case -0x7ff8fb0f:
            goto switchD_005c0604_caseD_800704f1;
          case -0x7ff8fb09:
            goto switchD_005c0604_caseD_800704f7;
          case -0x7ff8fb07:
            goto switchD_005c0604_caseD_800704f9;
          case -0x7ff8fb06:
            goto switchD_005c0604_caseD_800704fa;
          case -0x7ff8fb05:
            goto switchD_005c0604_caseD_800704fb;
          case -0x7ff8fb04:
            goto switchD_005c0604_caseD_800704fc;
          case -0x7ff8fb03:
            goto switchD_005c0604_caseD_800704fd;
          case -0x7ff8fb02:
            goto switchD_005c0604_caseD_800704fe;
          case -0x7ff8fb01:
            goto switchD_005c0604_caseD_800704ff;
          case -0x7ff8fb00:
            goto switchD_005c0604_caseD_80070500;
          case -0x7ff8faff:
            goto switchD_005c0604_caseD_80070501;
          case -0x7ff8fafe:
            goto switchD_005c0604_caseD_80070502;
          case -0x7ff8fafd:
            goto switchD_005c0604_caseD_80070503;
          case -0x7ff8fafc:
            goto switchD_005c0604_caseD_80070504;
          case -0x7ff8fafb:
            goto switchD_005c0604_caseD_80070505;
          case -0x7ff8faec:
            goto switchD_005c0604_caseD_80070514;
          case -0x7ff8faeb:
            goto switchD_005c0604_caseD_80070515;
          case -0x7ff8faea:
            goto switchD_005c0604_caseD_80070516;
          case -0x7ff8fae9:
            goto switchD_005c0604_caseD_80070517;
          case -0x7ff8fae8:
            goto LAB_005c9c66;
          case -0x7ff8fae7:
            goto switchD_005c0604_caseD_80070519;
          case -0x7ff8fae6:
            goto switchD_005c0604_caseD_8007051a;
          case -0x7ff8fae5:
            goto switchD_005c0604_caseD_8007051b;
          case -0x7ff8fae4:
            goto switchD_005c0604_caseD_8007051c;
          case -0x7ff8fae3:
            goto switchD_005c0604_caseD_8007051d;
          case -0x7ff8fae2:
            goto switchD_005c0604_caseD_8007051e;
          case -0x7ff8fae1:
            goto switchD_005c0604_caseD_8007051f;
          case -0x7ff8fae0:
            goto switchD_005c0604_caseD_80070520;
          case -0x7ff8fadf:
            goto switchD_005c0604_caseD_80070521;
          case -0x7ff8fade:
            goto switchD_005c0604_caseD_80070522;
          case -0x7ff8fadd:
            goto switchD_005c0604_caseD_80070523;
          case -0x7ff8fadc:
            goto switchD_005c0604_caseD_80070524;
          case -0x7ff8fadb:
            goto switchD_005c0604_caseD_80070525;
          case -0x7ff8fada:
            goto switchD_005c0604_caseD_80070526;
          case -0x7ff8fad9:
            goto switchD_005c0604_caseD_80070527;
          case -0x7ff8fad8:
            goto switchD_005c0604_caseD_80070528;
          case -0x7ff8fad7:
            goto switchD_005c0604_caseD_80070529;
          case -0x7ff8fad6:
            goto switchD_005c0604_caseD_8007052a;
          case -0x7ff8fad5:
            goto switchD_005c0604_caseD_8007052b;
          case -0x7ff8fad4:
            goto switchD_005c0604_caseD_8007052c;
          case -0x7ff8fad3:
            goto switchD_005c0604_caseD_8007052d;
          case -0x7ff8fad2:
            goto switchD_005c0604_caseD_8007052e;
          case -0x7ff8fad1:
            goto switchD_005c0604_caseD_8007052f;
          case -0x7ff8fad0:
            goto switchD_005c0604_caseD_80070530;
          case -0x7ff8facf:
            goto switchD_005c0604_caseD_80070531;
          case -0x7ff8face:
            goto switchD_005c0604_caseD_80070532;
          case -0x7ff8facd:
            goto switchD_005c0604_caseD_80070533;
          case -0x7ff8facc:
            goto switchD_005c0604_caseD_80070534;
          case -0x7ff8facb:
            goto switchD_005c0604_caseD_80070535;
          case -0x7ff8faca:
            goto switchD_005c0604_caseD_80070536;
          case -0x7ff8fac9:
            goto switchD_005c0604_caseD_80070537;
          case -0x7ff8fac8:
            goto switchD_005c0604_caseD_80070538;
          case -0x7ff8fac7:
            goto switchD_005c0604_caseD_80070539;
          case -0x7ff8fac6:
            goto switchD_005c0604_caseD_8007053a;
          case -0x7ff8fac4:
            goto switchD_005c0604_caseD_8007053c;
          case -0x7ff8fac3:
            goto switchD_005c0604_caseD_8007053d;
          case -0x7ff8fac2:
            goto switchD_005c0604_caseD_8007053e;
          case -0x7ff8fac1:
            goto switchD_005c0604_caseD_8007053f;
          case -0x7ff8fac0:
            goto switchD_005c0604_caseD_80070540;
          case -0x7ff8fabf:
            goto switchD_005c0604_caseD_80070541;
          case -0x7ff8fabe:
            goto switchD_005c0604_caseD_80070542;
          case -0x7ff8fabd:
            goto switchD_005c0604_caseD_80070543;
          case -0x7ff8fabc:
            goto switchD_005c0604_caseD_80070544;
          case -0x7ff8fabb:
            goto switchD_005c0604_caseD_80070545;
          case -0x7ff8faba:
            goto switchD_005c0604_caseD_80070546;
          case -0x7ff8fab9:
            goto switchD_005c0604_caseD_80070547;
          case -0x7ff8fab8:
            goto switchD_005c0604_caseD_80070548;
          case -0x7ff8fab7:
            goto switchD_005c0604_caseD_80070549;
          case -0x7ff8fab6:
            goto switchD_005c0604_caseD_8007054a;
          case -0x7ff8fab5:
            goto switchD_005c0604_caseD_8007054b;
          case -0x7ff8fab4:
            goto switchD_005c0604_caseD_8007054c;
          case -0x7ff8fab3:
            goto switchD_005c0604_caseD_8007054d;
          case -0x7ff8fab2:
            goto switchD_005c0604_caseD_8007054e;
          case -0x7ff8fab1:
            goto switchD_005c0604_caseD_8007054f;
          case -0x7ff8fab0:
            goto switchD_005c0604_caseD_80070550;
          case -0x7ff8faaf:
            goto switchD_005c0604_caseD_80070551;
          case -0x7ff8faae:
            goto switchD_005c0604_caseD_80070552;
          }
        }
      }
      else {
        switch(in_stack_00000004) {
        case -0x7ff8faac:
          goto switchD_005c061b_caseD_80070554;
        case -0x7ff8faab:
          goto switchD_005c061b_caseD_80070555;
        case -0x7ff8faaa:
          goto switchD_005c061b_caseD_80070556;
        case -0x7ff8faa9:
          goto switchD_005c061b_caseD_80070557;
        case -0x7ff8faa8:
          goto switchD_005c061b_caseD_80070558;
        case -0x7ff8faa7:
          goto switchD_005c061b_caseD_80070559;
        case -0x7ff8faa6:
          goto switchD_005c061b_caseD_8007055a;
        case -0x7ff8faa5:
          goto switchD_005c061b_caseD_8007055b;
        case -0x7ff8faa4:
          goto switchD_005c061b_caseD_8007055c;
        case -0x7ff8faa3:
          goto switchD_005c061b_caseD_8007055d;
        case -0x7ff8faa2:
          goto switchD_005c061b_caseD_8007055e;
        case -0x7ff8faa1:
          goto switchD_005c061b_caseD_8007055f;
        case -0x7ff8faa0:
          goto switchD_005c061b_caseD_80070560;
        case -0x7ff8fa9f:
          goto switchD_005c061b_caseD_80070561;
        case -0x7ff8fa9e:
          goto switchD_005c061b_caseD_80070562;
        case -0x7ff8fa9d:
          goto switchD_005c061b_caseD_80070563;
        case -0x7ff8fa9c:
          goto switchD_005c061b_caseD_80070564;
        case -0x7ff8fa9b:
          goto switchD_005c061b_caseD_80070565;
        case -0x7ff8fa9a:
          goto switchD_005c061b_caseD_80070566;
        case -0x7ff8fa99:
          goto switchD_005c061b_caseD_80070567;
        case -0x7ff8fa98:
          goto switchD_005c061b_caseD_80070568;
        case -0x7ff8fa97:
          goto switchD_005c061b_caseD_80070569;
        case -0x7ff8fa96:
          goto switchD_005c061b_caseD_8007056a;
        case -0x7ff8fa95:
          goto switchD_005c061b_caseD_8007056b;
        case -0x7ff8fa94:
          goto switchD_005c061b_caseD_8007056c;
        case -0x7ff8fa93:
          goto switchD_005c061b_caseD_8007056d;
        case -0x7ff8fa92:
          goto switchD_005c061b_caseD_8007056e;
        case -0x7ff8fa91:
          goto switchD_005c061b_caseD_8007056f;
        case -0x7ff8fa90:
          goto switchD_005c061b_caseD_80070570;
        case -0x7ff8fa8f:
          goto switchD_005c061b_caseD_80070571;
        case -0x7ff8fa8e:
          goto switchD_005c061b_caseD_80070572;
        case -0x7ff8fa8d:
          goto switchD_005c061b_caseD_80070573;
        case -0x7ff8fa8c:
          goto switchD_005c061b_caseD_80070574;
        case -0x7ff8fa8b:
          goto switchD_005c061b_caseD_80070575;
        case -0x7ff8fa8a:
          goto switchD_005c061b_caseD_80070576;
        case -0x7ff8fa89:
          goto switchD_005c061b_caseD_80070577;
        case -0x7ff8fa88:
          goto switchD_005c061b_caseD_80070578;
        case -0x7ff8fa87:
          goto switchD_005c061b_caseD_80070579;
        case -0x7ff8fa86:
          goto switchD_005c061b_caseD_8007057a;
        case -0x7ff8fa85:
          goto switchD_005c061b_caseD_8007057b;
        case -0x7ff8fa84:
          goto switchD_005c061b_caseD_8007057c;
        case -0x7ff8fa83:
          goto switchD_005c061b_caseD_8007057d;
        case -0x7ff8fa82:
          goto switchD_005c061b_caseD_8007057e;
        case -0x7ff8fa81:
          goto switchD_005c061b_caseD_8007057f;
        case -0x7ff8fa80:
          goto switchD_005c061b_caseD_80070580;
        case -0x7ff8fa7f:
          goto switchD_005c061b_caseD_80070581;
        case -0x7ff8fa7e:
          goto switchD_005c061b_caseD_80070582;
        case -0x7ff8fa7d:
          goto switchD_005c061b_caseD_80070583;
        case -0x7ff8fa7c:
          goto switchD_005c061b_caseD_80070584;
        case -0x7ff8fa7b:
          goto switchD_005c061b_caseD_80070585;
        case -0x7ff8fa7a:
          goto switchD_005c061b_caseD_80070586;
        case -0x7ff8fa79:
          goto switchD_005c061b_caseD_80070587;
        case -0x7ff8fa78:
          goto switchD_005c061b_caseD_80070588;
        case -0x7ff8fa77:
          goto switchD_005c061b_caseD_80070589;
        case -0x7ff8fa76:
          goto switchD_005c061b_caseD_8007058a;
        case -0x7ff8fa75:
          goto switchD_005c061b_caseD_8007058b;
        case -0x7ff8fa74:
          goto switchD_005c061b_caseD_8007058c;
        case -0x7ff8fa73:
          goto switchD_005c061b_caseD_8007058d;
        case -0x7ff8fa72:
          goto switchD_005c061b_caseD_8007058e;
        case -0x7ff8fa71:
          goto switchD_005c061b_caseD_8007058f;
        case -0x7ff8fa70:
          goto switchD_005c061b_caseD_80070590;
        case -0x7ff8fa6f:
          goto switchD_005c061b_caseD_80070591;
        case -0x7ff8fa6e:
          goto switchD_005c061b_caseD_80070592;
        case -0x7ff8fa6d:
          goto switchD_005c061b_caseD_80070593;
        case -0x7ff8fa6c:
          goto switchD_005c061b_caseD_80070594;
        case -0x7ff8fa6b:
          goto switchD_005c061b_caseD_80070595;
        case -0x7ff8fa6a:
          goto switchD_005c061b_caseD_80070596;
        case -0x7ff8fa69:
          goto switchD_005c061b_caseD_80070597;
        case -0x7ff8fa68:
          goto switchD_005c061b_caseD_80070598;
        case -0x7ff8fa67:
          goto switchD_005c061b_caseD_80070599;
        case -0x7ff8fa66:
          goto switchD_005c061b_caseD_8007059a;
        case -0x7ff8fa65:
          goto switchD_005c061b_caseD_8007059b;
        case -0x7ff8fa64:
          goto switchD_005c061b_caseD_8007059c;
        case -0x7ff8fa63:
          goto switchD_005c061b_caseD_8007059d;
        case -0x7ff8fa62:
          goto switchD_005c061b_caseD_8007059e;
        case -0x7ff8fa61:
          goto switchD_005c061b_caseD_8007059f;
        case -0x7ff8fa60:
          goto switchD_005c061b_caseD_800705a0;
        case -0x7ff8fa5f:
          goto switchD_005c061b_caseD_800705a1;
        case -0x7ff8fa5e:
          goto switchD_005c061b_caseD_800705a2;
        case -0x7ff8fa5d:
          goto switchD_005c061b_caseD_800705a3;
        case -0x7ff8fa5c:
          goto switchD_005c061b_caseD_800705a4;
        case -0x7ff8fa5b:
          goto switchD_005c061b_caseD_800705a5;
        case -0x7ff8fa5a:
          goto switchD_005c061b_caseD_800705a6;
        case -0x7ff8fa59:
          goto switchD_005c061b_caseD_800705a7;
        case -0x7ff8fa58:
          goto switchD_005c061b_caseD_800705a8;
        case -0x7ff8fa57:
          goto switchD_005c061b_caseD_800705a9;
        case -0x7ff8fa56:
          goto switchD_005c061b_caseD_800705aa;
        case -0x7ff8fa55:
          goto switchD_005c061b_caseD_800705ab;
        case -0x7ff8fa54:
          goto switchD_005c061b_caseD_800705ac;
        case -0x7ff8fa53:
          goto switchD_005c061b_caseD_800705ad;
        case -0x7ff8fa52:
          goto switchD_005c061b_caseD_800705ae;
        case -0x7ff8fa51:
          goto switchD_005c061b_caseD_800705af;
        case -0x7ff8fa50:
          goto switchD_005c061b_caseD_800705b0;
        case -0x7ff8fa4f:
          goto switchD_005c061b_caseD_800705b1;
        case -0x7ff8fa4e:
          goto switchD_005c061b_caseD_800705b2;
        case -0x7ff8fa4d:
          goto switchD_005c061b_caseD_800705b3;
        case -0x7ff8fa4c:
          goto switchD_005c061b_caseD_800705b4;
        case -0x7ff8fa4b:
          goto switchD_005c061b_caseD_800705b5;
        case -0x7ff8fa24:
          goto switchD_005c061b_caseD_800705dc;
        case -0x7ff8fa23:
          goto switchD_005c061b_caseD_800705dd;
        case -0x7ff8fa22:
          goto switchD_005c061b_caseD_800705de;
        case -0x7ff8fa21:
          goto switchD_005c061b_caseD_800705df;
        case -0x7ff8f9bf:
          goto switchD_005c061b_caseD_80070641;
        case -0x7ff8f9be:
          goto switchD_005c061b_caseD_80070642;
        case -0x7ff8f9bd:
          goto switchD_005c061b_caseD_80070643;
        case -0x7ff8f9bc:
          goto switchD_005c061b_caseD_80070644;
        case -0x7ff8f9bb:
          goto switchD_005c061b_caseD_80070645;
        case -0x7ff8f9ba:
          goto switchD_005c061b_caseD_80070646;
        case -0x7ff8f9b9:
          goto switchD_005c061b_caseD_80070647;
        case -0x7ff8f9b8:
          goto switchD_005c061b_caseD_80070648;
        case -0x7ff8f9b7:
          goto switchD_005c061b_caseD_80070649;
        case -0x7ff8f9b6:
          goto switchD_005c061b_caseD_8007064a;
        case -0x7ff8f9b5:
          goto switchD_005c061b_caseD_8007064b;
        case -0x7ff8f9b4:
          goto switchD_005c061b_caseD_8007064c;
        case -0x7ff8f9b3:
          goto switchD_005c061b_caseD_8007064d;
        case -0x7ff8f9b2:
          goto switchD_005c061b_caseD_8007064e;
        case -0x7ff8f9b1:
          goto switchD_005c061b_caseD_8007064f;
        case -0x7ff8f9b0:
          goto switchD_005c061b_caseD_80070650;
        case -0x7ff8f9af:
          goto switchD_005c061b_caseD_80070651;
        case -0x7ff8f9ae:
          goto switchD_005c061b_caseD_80070652;
        case -0x7ff8f9ad:
          goto switchD_005c061b_caseD_80070653;
        case -0x7ff8f9ac:
          goto switchD_005c061b_caseD_80070654;
        case -0x7ff8f9ab:
          goto switchD_005c061b_caseD_80070655;
        case -0x7ff8f9aa:
          goto switchD_005c061b_caseD_80070656;
        case -0x7ff8f9a9:
          goto switchD_005c061b_caseD_80070657;
        case -0x7ff8f9a8:
          goto switchD_005c061b_caseD_80070658;
        case -0x7ff8f9a7:
          goto switchD_005c061b_caseD_80070659;
        case -0x7ff8f9a6:
          goto switchD_005c061b_caseD_8007065a;
        case -0x7ff8f9a5:
          goto switchD_005c061b_caseD_8007065b;
        case -0x7ff8f9a4:
          goto switchD_005c061b_caseD_8007065c;
        case -0x7ff8f9a3:
          goto switchD_005c061b_caseD_8007065d;
        case -0x7ff8f9a2:
          goto switchD_005c061b_caseD_8007065e;
        case -0x7ff8f9a1:
          goto switchD_005c061b_caseD_8007065f;
        case -0x7ff8f9a0:
          goto switchD_005c061b_caseD_80070660;
        case -0x7ff8f99f:
          goto switchD_005c061b_caseD_80070661;
        case -0x7ff8f99e:
          goto switchD_005c061b_caseD_80070662;
        case -0x7ff8f99d:
          goto switchD_005c061b_caseD_80070663;
        case -0x7ff8f99c:
          goto switchD_005c061b_caseD_80070664;
        case -0x7ff8f99b:
          goto switchD_005c061b_caseD_80070665;
        case -0x7ff8f99a:
          goto switchD_005c061b_caseD_80070666;
        case -0x7ff8f999:
          goto switchD_005c061b_caseD_80070667;
        case -0x7ff8f998:
          goto switchD_005c061b_caseD_80070668;
        case -0x7ff8f997:
          goto switchD_005c061b_caseD_80070669;
        case -0x7ff8f996:
          goto switchD_005c061b_caseD_8007066a;
        case -0x7ff8f995:
          goto switchD_005c061b_caseD_8007066b;
        case -0x7ff8f994:
          goto switchD_005c061b_caseD_8007066c;
        case -0x7ff8f993:
          goto switchD_005c061b_caseD_8007066d;
        case -0x7ff8f95c:
          goto switchD_005c061b_caseD_800706a4;
        case -0x7ff8f95b:
          goto switchD_005c061b_caseD_800706a5;
        case -0x7ff8f95a:
          goto switchD_005c061b_caseD_800706a6;
        case -0x7ff8f959:
          goto switchD_005c061b_caseD_800706a7;
        case -0x7ff8f958:
          goto switchD_005c061b_caseD_800706a8;
        case -0x7ff8f957:
          goto switchD_005c061b_caseD_800706a9;
        case -0x7ff8f956:
          goto switchD_005c061b_caseD_800706aa;
        case -0x7ff8f955:
          goto switchD_005c061b_caseD_800706ab;
        case -0x7ff8f954:
          goto switchD_005c061b_caseD_800706ac;
        case -0x7ff8f953:
          goto switchD_005c061b_caseD_800706ad;
        case -0x7ff8f952:
          goto switchD_005c061b_caseD_800706ae;
        case -0x7ff8f951:
          goto switchD_005c061b_caseD_800706af;
        case -0x7ff8f950:
          goto switchD_005c061b_caseD_800706b0;
        case -0x7ff8f94f:
          goto switchD_005c061b_caseD_800706b1;
        case -0x7ff8f94e:
          goto switchD_005c061b_caseD_800706b2;
        case -0x7ff8f94d:
          goto switchD_005c061b_caseD_800706b3;
        case -0x7ff8f94c:
          goto switchD_005c061b_caseD_800706b4;
        case -0x7ff8f94b:
          goto switchD_005c061b_caseD_800706b5;
        case -0x7ff8f94a:
          goto switchD_005c061b_caseD_800706b6;
        case -0x7ff8f949:
          goto switchD_005c061b_caseD_800706b7;
        case -0x7ff8f948:
          goto switchD_005c061b_caseD_800706b8;
        case -0x7ff8f947:
          goto switchD_005c061b_caseD_800706b9;
        case -0x7ff8f946:
          goto switchD_005c061b_caseD_800706ba;
        case -0x7ff8f945:
          goto switchD_005c061b_caseD_800706bb;
        case -0x7ff8f944:
          goto switchD_005c061b_caseD_800706bc;
        case -0x7ff8f943:
          goto switchD_005c061b_caseD_800706bd;
        case -0x7ff8f942:
          goto switchD_005c061b_caseD_800706be;
        case -0x7ff8f941:
          goto switchD_005c061b_caseD_800706bf;
        case -0x7ff8f940:
          goto switchD_005c061b_caseD_800706c0;
        case -0x7ff8f93e:
          goto switchD_005c061b_caseD_800706c2;
        case -0x7ff8f93c:
          goto switchD_005c061b_caseD_800706c4;
        case -0x7ff8f93b:
          goto switchD_005c061b_caseD_800706c5;
        case -0x7ff8f93a:
          goto switchD_005c061b_caseD_800706c6;
        case -0x7ff8f939:
          goto switchD_005c061b_caseD_800706c7;
        case -0x7ff8f938:
          goto switchD_005c061b_caseD_800706c8;
        case -0x7ff8f937:
          goto switchD_005c061b_caseD_800706c9;
        case -0x7ff8f935:
          goto switchD_005c061b_caseD_800706cb;
        case -0x7ff8f934:
          goto switchD_005c061b_caseD_800706cc;
        case -0x7ff8f933:
          goto switchD_005c061b_caseD_800706cd;
        case -0x7ff8f932:
          goto switchD_005c061b_caseD_800706ce;
        case -0x7ff8f931:
          goto switchD_005c061b_caseD_800706cf;
        case -0x7ff8f930:
          goto switchD_005c061b_caseD_800706d0;
        case -0x7ff8f92f:
          goto switchD_005c061b_caseD_800706d1;
        case -0x7ff8f92e:
          goto switchD_005c061b_caseD_800706d2;
        case -0x7ff8f92d:
          goto switchD_005c061b_caseD_800706d3;
        case -0x7ff8f92c:
          goto switchD_005c061b_caseD_800706d4;
        case -0x7ff8f92b:
          goto switchD_005c061b_caseD_800706d5;
        case -0x7ff8f92a:
          goto switchD_005c061b_caseD_800706d6;
        case -0x7ff8f929:
          goto switchD_005c061b_caseD_800706d7;
        case -0x7ff8f928:
          goto switchD_005c061b_caseD_800706d8;
        case -0x7ff8f927:
          goto switchD_005c061b_caseD_800706d9;
        case -0x7ff8f926:
          goto switchD_005c061b_caseD_800706da;
        case -0x7ff8f925:
          goto switchD_005c061b_caseD_800706db;
        case -0x7ff8f924:
          goto switchD_005c061b_caseD_800706dc;
        case -0x7ff8f923:
          goto switchD_005c061b_caseD_800706dd;
        case -0x7ff8f922:
          goto switchD_005c061b_caseD_800706de;
        case -0x7ff8f921:
          goto switchD_005c061b_caseD_800706df;
        case -0x7ff8f920:
          goto switchD_005c061b_caseD_800706e0;
        case -0x7ff8f91f:
          goto switchD_005c061b_caseD_800706e1;
        case -0x7ff8f91e:
          goto switchD_005c061b_caseD_800706e2;
        case -0x7ff8f91d:
          goto switchD_005c061b_caseD_800706e3;
        case -0x7ff8f91c:
          goto switchD_005c061b_caseD_800706e4;
        case -0x7ff8f91b:
          goto switchD_005c061b_caseD_800706e5;
        case -0x7ff8f91a:
          goto switchD_005c061b_caseD_800706e6;
        case -0x7ff8f919:
          goto switchD_005c061b_caseD_800706e7;
        case -0x7ff8f918:
          goto switchD_005c061b_caseD_800706e8;
        case -0x7ff8f917:
          goto switchD_005c061b_caseD_800706e9;
        case -0x7ff8f916:
          goto switchD_005c061b_caseD_800706ea;
        case -0x7ff8f915:
          goto switchD_005c061b_caseD_800706eb;
        case -0x7ff8f914:
          goto switchD_005c061b_caseD_800706ec;
        case -0x7ff8f913:
          goto switchD_005c061b_caseD_800706ed;
        case -0x7ff8f912:
          goto switchD_005c061b_caseD_800706ee;
        case -0x7ff8f911:
          goto switchD_005c061b_caseD_800706ef;
        case -0x7ff8f90f:
          goto switchD_005c061b_caseD_800706f1;
        case -0x7ff8f90e:
          goto switchD_005c061b_caseD_800706f2;
        case -0x7ff8f90d:
          goto switchD_005c061b_caseD_800706f3;
        case -0x7ff8f90c:
          goto switchD_005c061b_caseD_800706f4;
        case -0x7ff8f90b:
          goto switchD_005c061b_caseD_800706f5;
        case -0x7ff8f90a:
          goto switchD_005c061b_caseD_800706f6;
        case -0x7ff8f909:
          goto switchD_005c061b_caseD_800706f7;
        case -0x7ff8f908:
          goto switchD_005c061b_caseD_800706f8;
        case -0x7ff8f907:
          goto switchD_005c061b_caseD_800706f9;
        case -0x7ff8f906:
          goto switchD_005c061b_caseD_800706fa;
        case -0x7ff8f905:
          goto switchD_005c061b_caseD_800706fb;
        case -0x7ff8f904:
          goto switchD_005c061b_caseD_800706fc;
        case -0x7ff8f903:
          goto switchD_005c061b_caseD_800706fd;
        case -0x7ff8f902:
          goto switchD_005c061b_caseD_800706fe;
        case -0x7ff8f901:
          goto switchD_005c061b_caseD_800706ff;
        case -0x7ff8f900:
          goto switchD_005c061b_caseD_80070700;
        case -0x7ff8f8ff:
          goto switchD_005c061b_caseD_80070701;
        case -0x7ff8f8fe:
          goto switchD_005c061b_caseD_80070702;
        case -0x7ff8f8fd:
          goto switchD_005c061b_caseD_80070703;
        case -0x7ff8f8fc:
          goto switchD_005c061b_caseD_80070704;
        case -0x7ff8f8fb:
          goto switchD_005c061b_caseD_80070705;
        case -0x7ff8f8fa:
          goto switchD_005c061b_caseD_80070706;
        case -0x7ff8f8f9:
          goto switchD_005c061b_caseD_80070707;
        case -0x7ff8f8f8:
          goto switchD_005c061b_caseD_80070708;
        case -0x7ff8f8f7:
          goto switchD_005c061b_caseD_80070709;
        case -0x7ff8f8f6:
          goto switchD_005c061b_caseD_8007070a;
        case -0x7ff8f8f5:
          goto switchD_005c061b_caseD_8007070b;
        case -0x7ff8f8f4:
          goto switchD_005c061b_caseD_8007070c;
        case -0x7ff8f8f3:
          goto switchD_005c061b_caseD_8007070d;
        case -0x7ff8f8f2:
          goto switchD_005c061b_caseD_8007070e;
        case -0x7ff8f8f1:
          goto switchD_005c061b_caseD_8007070f;
        case -0x7ff8f8f0:
          goto switchD_005c061b_caseD_80070710;
        case -0x7ff8f8ef:
          goto switchD_005c061b_caseD_80070711;
        case -0x7ff8f8ee:
          goto switchD_005c061b_caseD_80070712;
        case -0x7ff8f8ed:
          goto switchD_005c061b_caseD_80070713;
        case -0x7ff8f8ec:
          goto switchD_005c061b_caseD_80070714;
        case -0x7ff8f8eb:
          goto switchD_005c061b_caseD_80070715;
        case -0x7ff8f8ea:
          goto switchD_005c061b_caseD_80070716;
        case -0x7ff8f8e9:
          goto switchD_005c061b_caseD_80070717;
        case -0x7ff8f8e8:
          goto switchD_005c061b_caseD_80070718;
        case -0x7ff8f8e7:
          goto switchD_005c061b_caseD_80070719;
        case -0x7ff8f8e6:
          goto switchD_005c061b_caseD_8007071a;
        case -0x7ff8f8e5:
          goto switchD_005c061b_caseD_8007071b;
        case -0x7ff8f8e4:
          goto switchD_005c061b_caseD_8007071c;
        case -0x7ff8f8e3:
          goto switchD_005c061b_caseD_8007071d;
        case -0x7ff8f8e2:
          goto switchD_005c061b_caseD_8007071e;
        case -0x7ff8f8e1:
          goto switchD_005c061b_caseD_8007071f;
        case -0x7ff8f8e0:
          goto switchD_005c061b_caseD_80070720;
        case -0x7ff8f8df:
          goto switchD_005c061b_caseD_80070721;
        case -0x7ff8f8de:
          goto switchD_005c061b_caseD_80070722;
        case -0x7ff8f8dd:
          goto switchD_005c061b_caseD_80070723;
        case -0x7ff8f8dc:
          goto switchD_005c061b_caseD_80070724;
        case -0x7ff8f8db:
          goto switchD_005c061b_caseD_80070725;
        case -0x7ff8f8da:
          goto switchD_005c061b_caseD_80070726;
        case -0x7ff8f8d9:
          goto switchD_005c061b_caseD_80070727;
        case -0x7ff8f8d8:
          goto switchD_005c061b_caseD_80070728;
        case -0x7ff8f896:
          goto switchD_005c061b_caseD_8007076a;
        case -0x7ff8f895:
          goto switchD_005c061b_caseD_8007076b;
        case -0x7ff8f894:
          goto switchD_005c061b_caseD_8007076c;
        case -0x7ff8f893:
          goto switchD_005c061b_caseD_8007076d;
        case -0x7ff8f892:
          goto switchD_005c061b_caseD_8007076e;
        case -0x7ff8f891:
          goto switchD_005c061b_caseD_8007076f;
        case -0x7ff8f890:
          goto switchD_005c061b_caseD_80070770;
        case -0x7ff8f88f:
          goto switchD_005c061b_caseD_80070771;
        case -0x7ff8f88e:
          goto switchD_005c061b_caseD_80070772;
        case -0x7ff8f88d:
          goto switchD_005c061b_caseD_80070773;
        case -0x7ff8f88c:
          goto switchD_005c061b_caseD_80070774;
        case -0x7ff8f88b:
          goto switchD_005c061b_caseD_80070775;
        case -0x7ff8f88a:
          goto switchD_005c061b_caseD_80070776;
        case -0x7ff8f889:
          goto switchD_005c061b_caseD_80070777;
        case -0x7ff8f888:
          goto switchD_005c061b_caseD_80070778;
        case -0x7ff8f887:
          goto switchD_005c061b_caseD_80070779;
        case -0x7ff8f886:
          goto switchD_005c061b_caseD_8007077a;
        case -0x7ff8f885:
          goto switchD_005c061b_caseD_8007077b;
        }
      }
    }
    else if (in_stack_00000004 < -0x7ff8f82f) {
      if (in_stack_00000004 == -0x7ff8f830) {
switchD_005c6079_caseD_7d0:
        return (int)"ERROR_INVALID_PIXEL_FORMAT";
      }
      switch(in_stack_00000004) {
      case -0x7ff8f883:
        goto switchD_005c063f_caseD_8007077d;
      case -0x7ff8f882:
        goto switchD_005c063f_caseD_8007077e;
      case -0x7ff8f881:
        goto switchD_005c063f_caseD_8007077f;
      case -0x7ff8f880:
        goto switchD_005c063f_caseD_80070780;
      case -0x7ff8f87f:
        goto switchD_005c063f_caseD_80070781;
      case -0x7ff8f87e:
        goto switchD_005c063f_caseD_80070782;
      case -0x7ff8f87d:
        goto switchD_005c063f_caseD_80070783;
      case -0x7ff8f87c:
        goto switchD_005c063f_caseD_80070784;
      case -0x7ff8f87b:
        goto switchD_005c063f_caseD_80070785;
      case -0x7ff8f87a:
        goto switchD_005c063f_caseD_80070786;
      case -0x7ff8f879:
        goto switchD_005c063f_caseD_80070787;
      case -0x7ff8f878:
        goto switchD_005c063f_caseD_80070788;
      case -0x7ff8f877:
        goto switchD_005c063f_caseD_80070789;
      case -0x7ff8f876:
        goto switchD_005c063f_caseD_8007078a;
      case -0x7ff8f875:
        goto switchD_005c063f_caseD_8007078b;
      case -0x7ff8f874:
        goto switchD_005c063f_caseD_8007078c;
      case -0x7ff8f873:
        goto switchD_005c063f_caseD_8007078d;
      case -0x7ff8f872:
        goto switchD_005c063f_caseD_8007078e;
      }
    }
    else if (in_stack_00000004 < -0x7ff8f7c3) {
      if (in_stack_00000004 == -0x7ff8f7c4) goto switchD_005c6079_caseD_83c;
      switch(in_stack_00000004) {
      case -0x7ff8f82f:
        goto switchD_005c0663_caseD_800707d1;
      case -0x7ff8f82e:
        goto switchD_005c0663_caseD_800707d2;
      case -0x7ff8f82d:
        goto switchD_005c0663_caseD_800707d3;
      case -0x7ff8f82c:
        goto switchD_005c0663_caseD_800707d4;
      case -0x7ff8f82b:
        goto switchD_005c0663_caseD_800707d5;
      case -0x7ff8f826:
        goto switchD_005c0663_caseD_800707da;
      case -0x7ff8f825:
        goto switchD_005c0663_caseD_800707db;
      case -0x7ff8f824:
        goto switchD_005c0663_caseD_800707dc;
      case -0x7ff8f823:
        goto switchD_005c0663_caseD_800707dd;
      case -0x7ff8f822:
        goto switchD_005c0663_caseD_800707de;
      case -0x7ff8f821:
        goto switchD_005c0663_caseD_800707df;
      case -0x7ff8f820:
        goto switchD_005c0663_caseD_800707e0;
      case -0x7ff8f81f:
        goto switchD_005c0663_caseD_800707e1;
      case -0x7ff8f81e:
        goto switchD_005c0663_caseD_800707e2;
      case -0x7ff8f81d:
        goto switchD_005c0663_caseD_800707e3;
      case -0x7ff8f81c:
        goto switchD_005c0663_caseD_800707e4;
      case -0x7ff8f81b:
        goto switchD_005c0663_caseD_800707e5;
      case -0x7ff8f81a:
        goto switchD_005c0663_caseD_800707e6;
      }
    }
    else if (in_stack_00000004 < -0x7ff8de5c) {
      if (in_stack_00000004 == -0x7ff8de5d) {
switchD_005c81e1_caseD_21a3:
        return (int)"ERROR_DS_WKO_CONTAINER_CANNOT_BE_SPECIAL";
      }
      if (in_stack_00000004 < -0x7ff8dfc6) {
        if (in_stack_00000004 == -0x7ff8dfc7) goto switchD_005c768d_caseD_2039;
        if (in_stack_00000004 < -0x7ff8ec32) {
          if (in_stack_00000004 == -0x7ff8ec33) {
switchD_005c6f3d_caseD_13cd:
            return (int)"ERROR_DEPENDENCY_NOT_ALLOWED";
          }
          if (in_stack_00000004 < -0x7ff8ef0f) {
            if (in_stack_00000004 == -0x7ff8ef10) {
switchD_005c6bc5_caseD_10f0:
              return (int)"ERROR_MESSAGE_EXCEEDS_MAX_SIZE";
            }
            if (in_stack_00000004 < -0x7ff8ef8c) {
              if (in_stack_00000004 == -0x7ff8ef8d) goto switchD_005c6a2e_caseD_1073;
              if (in_stack_00000004 < -0x7ff8f439) {
                if (in_stack_00000004 == -0x7ff8f43a) goto LAB_005c690b;
                if (in_stack_00000004 < -0x7ff8f443) {
                  if (in_stack_00000004 == -0x7ff8f444) {
LAB_005c6888:
                    return (int)"ERROR_SPL_NO_ADDJOB";
                  }
                  if (in_stack_00000004 < -0x7ff8f69b) {
                    if (in_stack_00000004 == -0x7ff8f69c) {
LAB_005c6855:
                      return (int)"ERROR_DEVICE_IN_USE";
                    }
                    if (in_stack_00000004 == -0x7ff8f7c3) goto switchD_005c6079_caseD_83d;
                    if (in_stack_00000004 == -0x7ff8f766) goto switchD_005c6079_caseD_89a;
                    if (in_stack_00000004 == -0x7ff8f736) goto LAB_005c679c;
                    if (in_stack_00000004 == -0x7ff8f69f) goto LAB_005c685f;
                    if (in_stack_00000004 == -0x7ff8f69e) goto LAB_005c0731;
                  }
                  else {
                    if (in_stack_00000004 == -0x7ff8f448) {
LAB_005c684b:
                      return (int)"ERROR_UNKNOWN_PRINT_MONITOR";
                    }
                    if (in_stack_00000004 == -0x7ff8f447) goto LAB_005c6869;
                    if (in_stack_00000004 == -0x7ff8f446) goto LAB_005c6892;
                    if (in_stack_00000004 == -0x7ff8f445) goto LAB_005c0767;
                  }
                }
                else {
                  switch(in_stack_00000004) {
                  case -0x7ff8f443:
                    goto switchD_005c077f_caseD_80070bbd;
                  case -0x7ff8f442:
                    goto switchD_005c077f_caseD_80070bbe;
                  case -0x7ff8f441:
                    goto switchD_005c077f_caseD_80070bbf;
                  case -0x7ff8f440:
                    goto switchD_005c077f_caseD_80070bc0;
                  case -0x7ff8f43f:
                    goto switchD_005c077f_caseD_80070bc1;
                  case -0x7ff8f43e:
                    goto switchD_005c077f_caseD_80070bc2;
                  case -0x7ff8f43d:
                    goto switchD_005c077f_caseD_80070bc3;
                  case -0x7ff8f43c:
                    goto switchD_005c077f_caseD_80070bc4;
                  case -0x7ff8f43b:
                    goto switchD_005c077f_caseD_80070bc5;
                  }
                }
              }
              else if (in_stack_00000004 < -0x7ff8ef96) {
                if (in_stack_00000004 == -0x7ff8ef97) goto switchD_005c69b8_caseD_1069;
                if (in_stack_00000004 < -0x7ff8f05b) {
                  if (in_stack_00000004 == -0x7ff8f05c) goto LAB_005c696f;
                  if (in_stack_00000004 == -0x7ff8f060) goto LAB_005c6965;
                  if (in_stack_00000004 == -0x7ff8f05f) goto LAB_005c695b;
                  if (in_stack_00000004 == -0x7ff8f05e) goto LAB_005c6951;
                  if (in_stack_00000004 == -0x7ff8f05d) goto LAB_005c6947;
                }
                else {
                  if (in_stack_00000004 == -0x7ff8f05b) goto LAB_005c69a0;
                  if (in_stack_00000004 == -0x7ff8f05a) goto LAB_005c6996;
                  if (in_stack_00000004 == -0x7ff8effc) goto LAB_005c698c;
                  if (in_stack_00000004 == -0x7ff8ef98) goto LAB_005c0801;
                }
              }
              else {
                switch(in_stack_00000004) {
                case -0x7ff8ef96:
                  goto switchD_005c0819_caseD_8007106a;
                case -0x7ff8ef95:
                  goto switchD_005c0819_caseD_8007106b;
                case -0x7ff8ef94:
                  goto switchD_005c0819_caseD_8007106c;
                case -0x7ff8ef93:
                  goto switchD_005c0819_caseD_8007106d;
                case -0x7ff8ef92:
                  goto switchD_005c0819_caseD_8007106e;
                case -0x7ff8ef91:
                  goto switchD_005c0819_caseD_8007106f;
                case -0x7ff8ef90:
                  goto switchD_005c0819_caseD_80071070;
                case -0x7ff8ef8f:
                  goto switchD_005c0819_caseD_80071071;
                case -0x7ff8ef8e:
                  goto switchD_005c0819_caseD_80071072;
                }
              }
            }
            else {
              switch(in_stack_00000004) {
              case -0x7ff8ef8c:
                goto switchD_005c0835_caseD_80071074;
              case -0x7ff8ef8b:
                goto switchD_005c0835_caseD_80071075;
              case -0x7ff8ef8a:
                goto switchD_005c0835_caseD_80071076;
              case -0x7ff8ef34:
                goto switchD_005c0835_caseD_800710cc;
              case -0x7ff8ef33:
                goto switchD_005c0835_caseD_800710cd;
              case -0x7ff8ef32:
                goto switchD_005c0835_caseD_800710ce;
              case -0x7ff8ef31:
                goto switchD_005c0835_caseD_800710cf;
              case -0x7ff8ef30:
                goto switchD_005c0835_caseD_800710d0;
              case -0x7ff8ef2f:
                goto switchD_005c0835_caseD_800710d1;
              case -0x7ff8ef2e:
                goto switchD_005c0835_caseD_800710d2;
              case -0x7ff8ef2d:
                goto switchD_005c0835_caseD_800710d3;
              case -0x7ff8ef2c:
                goto switchD_005c0835_caseD_800710d4;
              case -0x7ff8ef2b:
                goto switchD_005c0835_caseD_800710d5;
              case -0x7ff8ef2a:
                goto switchD_005c0835_caseD_800710d6;
              case -0x7ff8ef29:
                goto switchD_005c0835_caseD_800710d7;
              case -0x7ff8ef28:
                goto switchD_005c0835_caseD_800710d8;
              case -0x7ff8ef27:
                goto switchD_005c0835_caseD_800710d9;
              case -0x7ff8ef26:
                goto switchD_005c0835_caseD_800710da;
              case -0x7ff8ef25:
                goto switchD_005c0835_caseD_800710db;
              case -0x7ff8ef24:
                goto switchD_005c0835_caseD_800710dc;
              case -0x7ff8ef23:
                goto switchD_005c0835_caseD_800710dd;
              case -0x7ff8ef22:
                goto switchD_005c0835_caseD_800710de;
              case -0x7ff8ef21:
                goto switchD_005c0835_caseD_800710df;
              case -0x7ff8ef20:
                goto switchD_005c0835_caseD_800710e0;
              case -0x7ff8ef1f:
                goto switchD_005c0835_caseD_800710e1;
              case -0x7ff8ef1e:
                goto switchD_005c0835_caseD_800710e2;
              case -0x7ff8ef1d:
                goto switchD_005c0835_caseD_800710e3;
              case -0x7ff8ef1c:
                goto switchD_005c0835_caseD_800710e4;
              case -0x7ff8ef1b:
                goto switchD_005c0835_caseD_800710e5;
              case -0x7ff8ef1a:
                goto switchD_005c0835_caseD_800710e6;
              case -0x7ff8ef19:
                goto switchD_005c0835_caseD_800710e7;
              case -0x7ff8ef18:
                goto switchD_005c0835_caseD_800710e8;
              case -0x7ff8ef17:
                goto switchD_005c0835_caseD_800710e9;
              case -0x7ff8ef16:
                goto switchD_005c0835_caseD_800710ea;
              case -0x7ff8ef15:
                goto switchD_005c0835_caseD_800710eb;
              case -0x7ff8ef14:
                goto switchD_005c0835_caseD_800710ec;
              case -0x7ff8ef13:
                goto switchD_005c0835_caseD_800710ed;
              case -0x7ff8ef12:
                goto switchD_005c0835_caseD_800710ee;
              case -0x7ff8ef11:
                goto switchD_005c0835_caseD_800710ef;
              }
            }
          }
          else if (in_stack_00000004 < -0x7ff8ec5b) {
            if (in_stack_00000004 == -0x7ff8ec5c) goto switchD_005c6df3_caseD_13a4;
            if (in_stack_00000004 < -0x7ff8ec6f) {
              if (in_stack_00000004 == -0x7ff8ec70) {
LAB_005c6d12:
                return (int)"ERROR_SHUTDOWN_CLUSTER";
              }
              if (in_stack_00000004 < -0x7ff8eed6) {
                if (in_stack_00000004 == -0x7ff8eed7) {
LAB_005c6ccc:
                  return (int)"ERROR_REPARSE_TAG_INVALID";
                }
                if (in_stack_00000004 < -0x7ff8ef00) {
                  if (in_stack_00000004 == -0x7ff8ef01) goto switchD_005c6bc5_caseD_10ff;
                  if (in_stack_00000004 == -0x7ff8ef0f) goto switchD_005c6bc5_caseD_10f1;
                  if (in_stack_00000004 == -0x7ff8ef0e) goto switchD_005c6bc5_caseD_10f2;
                  if (in_stack_00000004 == -0x7ff8ef0d) goto switchD_005c6bc5_caseD_10f3;
                  if (in_stack_00000004 == -0x7ff8ef0c) goto switchD_005c6bc5_caseD_10f4;
                  if (in_stack_00000004 == -0x7ff8ef02) goto switchD_005c6bc5_caseD_10fe;
                }
                else {
                  if (in_stack_00000004 == -0x7ff8ef00) goto switchD_005c6bc5_caseD_1100;
                  if (in_stack_00000004 == -0x7ff8eeda) goto LAB_005c6c44;
                  if (in_stack_00000004 == -0x7ff8eed9) goto LAB_005c6cd6;
                  if (in_stack_00000004 == -0x7ff8eed8) goto LAB_005c08ed;
                }
              }
              else if (in_stack_00000004 < -0x7ff8ec74) {
                if (in_stack_00000004 == -0x7ff8ec75) goto LAB_005c6ce0;
                if (in_stack_00000004 == -0x7ff8eed6) {
LAB_005c6cc2:
                  return (int)"ERROR_REPARSE_TAG_MISMATCH";
                }
                if (in_stack_00000004 == -0x7ff8ee6c) {
LAB_005c6cb8:
                  return (int)"ERROR_VOLUME_NOT_SIS_ENABLED";
                }
                if (in_stack_00000004 == -0x7ff8ec77) {
LAB_005c6cae:
                  return (int)"ERROR_DEPENDENT_RESOURCE_EXISTS";
                }
                if (in_stack_00000004 == -0x7ff8ec76) {
LAB_005c6ca4:
                  return (int)"ERROR_DEPENDENCY_NOT_FOUND";
                }
              }
              else {
                if (in_stack_00000004 == -0x7ff8ec74) goto LAB_005c6d30;
                if (in_stack_00000004 == -0x7ff8ec73) goto LAB_005c6d26;
                if (in_stack_00000004 == -0x7ff8ec72) goto LAB_005c6d1c;
                if (in_stack_00000004 == -0x7ff8ec71) goto LAB_005c0963;
              }
            }
            else {
              switch(in_stack_00000004) {
              case -0x7ff8ec6f:
switchD_005c097b_caseD_80071391:
                return (int)"ERROR_CANT_EVICT_ACTIVE_NODE";
              case -0x7ff8ec6e:
                goto switchD_005c097b_caseD_80071392;
              case -0x7ff8ec6d:
                goto switchD_005c097b_caseD_80071393;
              case -0x7ff8ec6c:
                goto switchD_005c097b_caseD_80071394;
              case -0x7ff8ec6b:
                goto switchD_005c097b_caseD_80071395;
              case -0x7ff8ec6a:
                goto switchD_005c097b_caseD_80071396;
              case -0x7ff8ec69:
                goto switchD_005c097b_caseD_80071397;
              case -0x7ff8ec68:
                goto switchD_005c097b_caseD_80071398;
              case -0x7ff8ec67:
                goto switchD_005c097b_caseD_80071399;
              case -0x7ff8ec66:
                goto switchD_005c097b_caseD_8007139a;
              case -0x7ff8ec65:
                goto switchD_005c097b_caseD_8007139b;
              case -0x7ff8ec64:
                goto switchD_005c097b_caseD_8007139c;
              case -0x7ff8ec63:
                goto switchD_005c097b_caseD_8007139d;
              case -0x7ff8ec62:
                goto switchD_005c097b_caseD_8007139e;
              case -0x7ff8ec61:
                goto switchD_005c097b_caseD_8007139f;
              case -0x7ff8ec60:
                goto switchD_005c097b_caseD_800713a0;
              case -0x7ff8ec5f:
                goto switchD_005c097b_caseD_800713a1;
              case -0x7ff8ec5e:
                goto switchD_005c097b_caseD_800713a2;
              case -0x7ff8ec5d:
                goto switchD_005c097b_caseD_800713a3;
              }
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7ff8ec5b:
              goto switchD_005c0990_caseD_800713a5;
            case -0x7ff8ec5a:
              goto switchD_005c0990_caseD_800713a6;
            case -0x7ff8ec59:
              goto switchD_005c0990_caseD_800713a7;
            case -0x7ff8ec58:
              goto switchD_005c0990_caseD_800713a8;
            case -0x7ff8ec57:
              goto switchD_005c0990_caseD_800713a9;
            case -0x7ff8ec56:
              goto switchD_005c0990_caseD_800713aa;
            case -0x7ff8ec55:
              goto switchD_005c0990_caseD_800713ab;
            case -0x7ff8ec54:
              goto switchD_005c0990_caseD_800713ac;
            case -0x7ff8ec53:
              goto switchD_005c0990_caseD_800713ad;
            case -0x7ff8ec52:
              goto switchD_005c0990_caseD_800713ae;
            case -0x7ff8ec51:
              goto switchD_005c0990_caseD_800713af;
            case -0x7ff8ec50:
              goto switchD_005c0990_caseD_800713b0;
            case -0x7ff8ec4f:
              goto switchD_005c0990_caseD_800713b1;
            case -0x7ff8ec4e:
              goto switchD_005c0990_caseD_800713b2;
            case -0x7ff8ec4d:
              goto switchD_005c0990_caseD_800713b3;
            case -0x7ff8ec4c:
              goto switchD_005c0990_caseD_800713b4;
            case -0x7ff8ec4b:
              goto switchD_005c0990_caseD_800713b5;
            case -0x7ff8ec4a:
              goto switchD_005c0990_caseD_800713b6;
            case -0x7ff8ec49:
              goto switchD_005c0990_caseD_800713b7;
            case -0x7ff8ec48:
              goto switchD_005c0990_caseD_800713b8;
            case -0x7ff8ec47:
              goto switchD_005c0990_caseD_800713b9;
            case -0x7ff8ec46:
              goto switchD_005c0990_caseD_800713ba;
            case -0x7ff8ec45:
              goto switchD_005c0990_caseD_800713bb;
            case -0x7ff8ec44:
              goto switchD_005c0990_caseD_800713bc;
            case -0x7ff8ec43:
              goto switchD_005c0990_caseD_800713bd;
            case -0x7ff8ec42:
              goto switchD_005c0990_caseD_800713be;
            case -0x7ff8ec40:
              goto switchD_005c0990_caseD_800713c0;
            case -0x7ff8ec3f:
              goto switchD_005c0990_caseD_800713c1;
            case -0x7ff8ec3e:
              goto switchD_005c0990_caseD_800713c2;
            case -0x7ff8ec3d:
              goto switchD_005c0990_caseD_800713c3;
            case -0x7ff8ec3c:
              goto switchD_005c0990_caseD_800713c4;
            case -0x7ff8ec3b:
              goto switchD_005c0990_caseD_800713c5;
            case -0x7ff8ec3a:
              goto switchD_005c0990_caseD_800713c6;
            case -0x7ff8ec39:
              goto switchD_005c0990_caseD_800713c7;
            case -0x7ff8ec38:
              goto switchD_005c0990_caseD_800713c8;
            case -0x7ff8ec37:
              goto switchD_005c0990_caseD_800713c9;
            case -0x7ff8ec36:
              goto switchD_005c0990_caseD_800713ca;
            case -0x7ff8ec35:
              goto switchD_005c0990_caseD_800713cb;
            case -0x7ff8ec34:
              goto switchD_005c0990_caseD_800713cc;
            }
          }
        }
        else if (in_stack_00000004 < -0x7ff8e8fd) {
          if (in_stack_00000004 == -0x7ff8e8fe) goto LAB_005c70a2;
          switch(in_stack_00000004) {
          case -0x7ff8ec32:
            goto switchD_005c09b4_caseD_800713ce;
          case -0x7ff8ec31:
            goto switchD_005c09b4_caseD_800713cf;
          case -0x7ff8ec30:
            goto switchD_005c09b4_caseD_800713d0;
          case -0x7ff8ec2f:
            goto switchD_005c09b4_caseD_800713d1;
          case -0x7ff8ec2e:
            goto switchD_005c09b4_caseD_800713d2;
          case -0x7ff8ec2d:
            goto switchD_005c09b4_caseD_800713d3;
          case -0x7ff8ec2c:
            goto switchD_005c09b4_caseD_800713d4;
          case -0x7ff8ec2b:
            goto switchD_005c09b4_caseD_800713d5;
          case -0x7ff8ec2a:
            goto switchD_005c09b4_caseD_800713d6;
          case -0x7ff8ec29:
            goto switchD_005c09b4_caseD_800713d7;
          case -0x7ff8ec28:
            goto switchD_005c09b4_caseD_800713d8;
          case -0x7ff8ec27:
            goto switchD_005c09b4_caseD_800713d9;
          case -0x7ff8ec26:
            goto switchD_005c09b4_caseD_800713da;
          case -0x7ff8ec25:
            goto switchD_005c09b4_caseD_800713db;
          case -0x7ff8ec24:
            goto switchD_005c09b4_caseD_800713dc;
          case -0x7ff8ec23:
            goto switchD_005c09b4_caseD_800713dd;
          case -0x7ff8ec22:
            goto switchD_005c09b4_caseD_800713de;
          case -0x7ff8ec21:
            goto switchD_005c09b4_caseD_800713df;
          case -0x7ff8ec20:
            goto switchD_005c09b4_caseD_800713e0;
          case -0x7ff8ec1f:
            goto switchD_005c09b4_caseD_800713e1;
          }
        }
        else if (in_stack_00000004 < -0x7ff8e88f) {
          if (in_stack_00000004 == -0x7ff8e890) goto LAB_005c716a;
          switch(in_stack_00000004) {
          case -0x7ff8e8fd:
            goto switchD_005c09d8_caseD_80071703;
          case -0x7ff8e8fc:
            goto switchD_005c09d8_caseD_80071704;
          case -0x7ff8e8fb:
            goto switchD_005c09d8_caseD_80071705;
          case -0x7ff8e8fa:
            goto switchD_005c09d8_caseD_80071706;
          case -0x7ff8e8f9:
            goto switchD_005c09d8_caseD_80071707;
          case -0x7ff8e8f8:
            goto switchD_005c09d8_caseD_80071708;
          case -0x7ff8e8f7:
            goto switchD_005c09d8_caseD_80071709;
          case -0x7ff8e8f6:
            goto switchD_005c09d8_caseD_8007170a;
          case -0x7ff8e8f5:
            goto switchD_005c09d8_caseD_8007170b;
          case -0x7ff8e8f4:
            goto switchD_005c09d8_caseD_8007170c;
          case -0x7ff8e8f3:
            goto switchD_005c09d8_caseD_8007170d;
          case -0x7ff8e8f2:
            goto switchD_005c09d8_caseD_8007170e;
          case -0x7ff8e8f1:
            goto switchD_005c09d8_caseD_8007170f;
          case -0x7ff8e8f0:
            goto switchD_005c09d8_caseD_80071710;
          case -0x7ff8e8ef:
            goto switchD_005c09d8_caseD_80071711;
          }
        }
        else if (in_stack_00000004 < -0x7ff8e819) {
          if (in_stack_00000004 == -0x7ff8e81a) goto LAB_005c723c;
          switch(in_stack_00000004) {
          case -0x7ff8e88f:
            goto switchD_005c09fc_caseD_80071771;
          case -0x7ff8e88e:
            goto switchD_005c09fc_caseD_80071772;
          case -0x7ff8e88d:
            goto switchD_005c09fc_caseD_80071773;
          case -0x7ff8e88c:
            goto switchD_005c09fc_caseD_80071774;
          case -0x7ff8e88b:
            goto switchD_005c09fc_caseD_80071775;
          case -0x7ff8e88a:
            goto switchD_005c09fc_caseD_80071776;
          case -0x7ff8e889:
            goto switchD_005c09fc_caseD_80071777;
          case -0x7ff8e888:
            goto switchD_005c09fc_caseD_80071778;
          case -0x7ff8e887:
            goto switchD_005c09fc_caseD_80071779;
          case -0x7ff8e886:
            goto switchD_005c09fc_caseD_8007177a;
          case -0x7ff8e885:
            goto switchD_005c09fc_caseD_8007177b;
          case -0x7ff8e884:
            goto switchD_005c09fc_caseD_8007177c;
          case -0x7ff8e883:
            goto switchD_005c09fc_caseD_8007177d;
          case -0x7ff8e882:
            goto switchD_005c09fc_caseD_8007177e;
          case -0x7ff8e881:
            goto switchD_005c09fc_caseD_8007177f;
          case -0x7ff8e880:
            goto switchD_005c09fc_caseD_80071780;
          }
        }
        else if (in_stack_00000004 < -0x7ff8e0b2) {
          if (in_stack_00000004 == -0x7ff8e0b3) {
switchD_005c750e_caseD_1f4d:
            return (int)"FRS_ERR_SYSVOL_POPULATE";
          }
          if (in_stack_00000004 < -0x7ff8e47e) {
            if (in_stack_00000004 == -0x7ff8e47f) goto switchD_005c738a_caseD_1b81;
            if (in_stack_00000004 < -0x7ff8e49a) {
              if (in_stack_00000004 == -0x7ff8e49b) goto switchD_005c731e_caseD_1b65;
              if (in_stack_00000004 < -0x7ff8e4a1) {
                if (in_stack_00000004 == -0x7ff8e4a2) goto LAB_005c72fc;
                if (in_stack_00000004 == -0x7ff8e7c8) goto LAB_005c72bc;
                if (in_stack_00000004 == -0x7ff8e4a7) goto LAB_005c72b2;
                if (in_stack_00000004 == -0x7ff8e4a6) goto LAB_005c72a8;
                if (in_stack_00000004 == -0x7ff8e4a5) goto LAB_005c729e;
                if (in_stack_00000004 == -0x7ff8e4a4) goto LAB_005c72c6;
                if (in_stack_00000004 == -0x7ff8e4a3) goto LAB_005c0a8b;
              }
              else {
                if (in_stack_00000004 == -0x7ff8e4a1) {
LAB_005c72f2:
                  return (int)"ERROR_CTX_CLOSE_PENDING";
                }
                if (in_stack_00000004 == -0x7ff8e4a0) {
LAB_005c72e8:
                  return (int)"ERROR_CTX_NO_OUTBUF";
                }
                if (in_stack_00000004 == -0x7ff8e49f) goto LAB_005c7306;
                if (in_stack_00000004 == -0x7ff8e49e) goto switchD_005c731e_caseD_1b62;
                if (in_stack_00000004 == -0x7ff8e49d) goto switchD_005c731e_caseD_1b63;
                if (in_stack_00000004 == -0x7ff8e49c) goto switchD_005c731e_caseD_1b64;
              }
            }
            else {
              switch(in_stack_00000004) {
              case -0x7ff8e49a:
                goto switchD_005c0af6_caseD_80071b66;
              case -0x7ff8e499:
                goto switchD_005c0af6_caseD_80071b67;
              case -0x7ff8e498:
                goto switchD_005c0af6_caseD_80071b68;
              case -0x7ff8e497:
                goto switchD_005c0af6_caseD_80071b69;
              case -0x7ff8e492:
                goto switchD_005c0af6_caseD_80071b6e;
              case -0x7ff8e491:
                goto switchD_005c0af6_caseD_80071b6f;
              case -0x7ff8e490:
                goto switchD_005c0af6_caseD_80071b70;
              case -0x7ff8e48f:
                goto switchD_005c0af6_caseD_80071b71;
              case -0x7ff8e485:
                goto switchD_005c0af6_caseD_80071b7b;
              case -0x7ff8e483:
                goto switchD_005c0af6_caseD_80071b7d;
              case -0x7ff8e482:
                goto switchD_005c0af6_caseD_80071b7e;
              case -0x7ff8e480:
                goto switchD_005c0af6_caseD_80071b80;
              }
            }
          }
          else if (in_stack_00000004 < -0x7ff8e0be) {
            if (in_stack_00000004 == -0x7ff8e0bf) {
LAB_005c74b0:
              return (int)"FRS_ERR_INVALID_API_SEQUENCE";
            }
            switch(in_stack_00000004) {
            case -0x7ff8e47e:
              goto switchD_005c0b1a_caseD_80071b82;
            case -0x7ff8e47c:
              goto switchD_005c0b1a_caseD_80071b84;
            case -0x7ff8e47b:
              goto switchD_005c0b1a_caseD_80071b85;
            case -0x7ff8e477:
              goto switchD_005c0b1a_caseD_80071b89;
            case -0x7ff8e476:
              goto switchD_005c0b1a_caseD_80071b8a;
            case -0x7ff8e475:
              goto switchD_005c0b1a_caseD_80071b8b;
            case -0x7ff8e474:
              goto switchD_005c0b1a_caseD_80071b8c;
            case -0x7ff8e473:
              goto switchD_005c0b1a_caseD_80071b8d;
            case -0x7ff8e472:
              goto switchD_005c0b1a_caseD_80071b8e;
            case -0x7ff8e471:
              goto switchD_005c0b1a_caseD_80071b8f;
            case -0x7ff8e470:
switchD_005c0b1a_caseD_80071b90:
              return (int)"ERROR_CTX_LICENSE_EXPIRED";
            case -0x7ff8e46f:
switchD_005c0b1a_caseD_80071b91:
              return (int)"ERROR_CTX_SHADOW_NOT_RUNNING";
            case -0x7ff8e46e:
switchD_005c0b1a_caseD_80071b92:
              return (int)"ERROR_CTX_SHADOW_ENDED_BY_MODE_CHANGE";
            case -0x7ff8e46d:
switchD_005c0b1a_caseD_80071b93:
              return (int)"ERROR_ACTIVATION_COUNT_EXCEEDED";
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7ff8e0be:
switchD_005c0b2f_caseD_80071f42:
              return (int)"FRS_ERR_STARTING_SERVICE";
            case -0x7ff8e0bd:
switchD_005c0b2f_caseD_80071f43:
              return (int)"FRS_ERR_STOPPING_SERVICE";
            case -0x7ff8e0bc:
switchD_005c0b2f_caseD_80071f44:
              return (int)"FRS_ERR_INTERNAL_API";
            case -0x7ff8e0bb:
switchD_005c0b2f_caseD_80071f45:
              return (int)"FRS_ERR_INTERNAL";
            case -0x7ff8e0ba:
              goto switchD_005c0b2f_caseD_80071f46;
            case -0x7ff8e0b9:
              goto switchD_005c0b2f_caseD_80071f47;
            case -0x7ff8e0b8:
              goto switchD_005c0b2f_caseD_80071f48;
            case -0x7ff8e0b7:
              goto switchD_005c0b2f_caseD_80071f49;
            case -0x7ff8e0b6:
              goto switchD_005c0b2f_caseD_80071f4a;
            case -0x7ff8e0b5:
              goto switchD_005c0b2f_caseD_80071f4b;
            case -0x7ff8e0b4:
              goto switchD_005c0b2f_caseD_80071f4c;
            }
          }
        }
        else {
          switch(in_stack_00000004) {
          case -0x7ff8e0b2:
switchD_005c0b4d_caseD_80071f4e:
            return (int)"FRS_ERR_SYSVOL_POPULATE_TIMEOUT";
          case -0x7ff8e0b1:
            goto switchD_005c0b4d_caseD_80071f4f;
          case -0x7ff8e0b0:
switchD_005c0b4d_caseD_80071f50:
            return (int)"FRS_ERR_SYSVOL_DEMOTE";
          case -0x7ff8e0af:
switchD_005c0b4d_caseD_80071f51:
            return (int)"FRS_ERR_INVALID_SERVICE_PARAMETER";
          case -0x7ff8dff8:
switchD_005c0b4d_caseD_80072008:
            return (int)"ERROR_DS_NOT_INSTALLED";
          case -0x7ff8dff7:
switchD_005c0b4d_caseD_80072009:
            return (int)"ERROR_DS_MEMBERSHIP_EVALUATED_LOCALLY";
          case -0x7ff8dff6:
switchD_005c0b4d_caseD_8007200a:
            return (int)"ERROR_DS_NO_ATTRIBUTE_OR_VALUE";
          case -0x7ff8dff5:
switchD_005c0b4d_caseD_8007200b:
            return (int)"ERROR_DS_INVALID_ATTRIBUTE_SYNTAX";
          case -0x7ff8dff4:
switchD_005c0b4d_caseD_8007200c:
            return (int)"ERROR_DS_ATTRIBUTE_TYPE_UNDEFINED";
          case -0x7ff8dff3:
switchD_005c0b4d_caseD_8007200d:
            return (int)"ERROR_DS_ATTRIBUTE_OR_VALUE_EXISTS";
          case -0x7ff8dff2:
switchD_005c0b4d_caseD_8007200e:
            return (int)"ERROR_DS_BUSY";
          case -0x7ff8dff1:
switchD_005c0b4d_caseD_8007200f:
            return (int)"ERROR_DS_UNAVAILABLE";
          case -0x7ff8dff0:
switchD_005c0b4d_caseD_80072010:
            return (int)"ERROR_DS_NO_RIDS_ALLOCATED";
          case -0x7ff8dfef:
switchD_005c0b4d_caseD_80072011:
            return (int)"ERROR_DS_NO_MORE_RIDS";
          case -0x7ff8dfee:
switchD_005c0b4d_caseD_80072012:
            return (int)"ERROR_DS_INCORRECT_ROLE_OWNER";
          case -0x7ff8dfed:
switchD_005c0b4d_caseD_80072013:
            return (int)"ERROR_DS_RIDMGR_INIT_ERROR";
          case -0x7ff8dfec:
switchD_005c0b4d_caseD_80072014:
            return (int)"ERROR_DS_OBJ_CLASS_VIOLATION";
          case -0x7ff8dfeb:
switchD_005c0b4d_caseD_80072015:
            return (int)"ERROR_DS_CANT_ON_NON_LEAF";
          case -0x7ff8dfea:
switchD_005c0b4d_caseD_80072016:
            return (int)"ERROR_DS_CANT_ON_RDN";
          case -0x7ff8dfe9:
            goto switchD_005c0b4d_caseD_80072017;
          case -0x7ff8dfe8:
            goto switchD_005c0b4d_caseD_80072018;
          case -0x7ff8dfe7:
            goto switchD_005c0b4d_caseD_80072019;
          case -0x7ff8dfe6:
            goto switchD_005c0b4d_caseD_8007201a;
          case -0x7ff8dfe5:
            goto switchD_005c0b4d_caseD_8007201b;
          case -0x7ff8dfe4:
            goto switchD_005c0b4d_caseD_8007201c;
          case -0x7ff8dfe3:
            goto switchD_005c0b4d_caseD_8007201d;
          case -0x7ff8dfe2:
            goto switchD_005c0b4d_caseD_8007201e;
          case -0x7ff8dfe0:
            goto switchD_005c0b4d_caseD_80072020;
          case -0x7ff8dfdf:
            goto switchD_005c0b4d_caseD_80072021;
          case -0x7ff8dfde:
            goto switchD_005c0b4d_caseD_80072022;
          case -0x7ff8dfdd:
            goto switchD_005c0b4d_caseD_80072023;
          case -0x7ff8dfdc:
            goto switchD_005c0b4d_caseD_80072024;
          case -0x7ff8dfdb:
            goto switchD_005c0b4d_caseD_80072025;
          case -0x7ff8dfda:
            goto switchD_005c0b4d_caseD_80072026;
          case -0x7ff8dfd9:
            goto switchD_005c0b4d_caseD_80072027;
          case -0x7ff8dfd8:
            goto switchD_005c0b4d_caseD_80072028;
          case -0x7ff8dfd7:
            goto switchD_005c0b4d_caseD_80072029;
          case -0x7ff8dfd6:
            goto switchD_005c0b4d_caseD_8007202a;
          case -0x7ff8dfd5:
            goto switchD_005c0b4d_caseD_8007202b;
          case -0x7ff8dfd4:
            goto switchD_005c0b4d_caseD_8007202c;
          case -0x7ff8dfd3:
            goto switchD_005c0b4d_caseD_8007202d;
          case -0x7ff8dfd2:
            goto switchD_005c0b4d_caseD_8007202e;
          case -0x7ff8dfd1:
            goto switchD_005c0b4d_caseD_8007202f;
          case -0x7ff8dfd0:
            goto switchD_005c0b4d_caseD_80072030;
          case -0x7ff8dfcf:
            goto switchD_005c0b4d_caseD_80072031;
          case -0x7ff8dfce:
            goto switchD_005c0b4d_caseD_80072032;
          case -0x7ff8dfcd:
            goto switchD_005c0b4d_caseD_80072033;
          case -0x7ff8dfcc:
            goto switchD_005c0b4d_caseD_80072034;
          case -0x7ff8dfcb:
            goto switchD_005c0b4d_caseD_80072035;
          case -0x7ff8dfca:
            goto switchD_005c0b4d_caseD_80072036;
          case -0x7ff8dfc9:
            goto switchD_005c0b4d_caseD_80072037;
          case -0x7ff8dfc8:
            goto switchD_005c0b4d_caseD_80072038;
          }
        }
      }
      else {
        switch(in_stack_00000004) {
        case -0x7ff8dfc6:
          goto switchD_005c0b64_caseD_8007203a;
        case -0x7ff8dfc5:
          goto switchD_005c0b64_caseD_8007203b;
        case -0x7ff8dfc4:
          goto switchD_005c0b64_caseD_8007203c;
        case -0x7ff8dfc3:
          goto switchD_005c0b64_caseD_8007203d;
        case -0x7ff8dfc2:
          goto switchD_005c0b64_caseD_8007203e;
        case -0x7ff8dfc1:
          goto switchD_005c0b64_caseD_8007203f;
        case -0x7ff8dfc0:
          goto switchD_005c0b64_caseD_80072040;
        case -0x7ff8dfbf:
          goto switchD_005c0b64_caseD_80072041;
        case -0x7ff8dfbe:
          goto switchD_005c0b64_caseD_80072042;
        case -0x7ff8dfbd:
          goto switchD_005c0b64_caseD_80072043;
        case -0x7ff8dfbc:
          goto switchD_005c0b64_caseD_80072044;
        case -0x7ff8dfbb:
          goto switchD_005c0b64_caseD_80072045;
        case -0x7ff8dfba:
          goto switchD_005c0b64_caseD_80072046;
        case -0x7ff8df93:
          goto switchD_005c0b64_caseD_8007206d;
        case -0x7ff8df92:
          goto switchD_005c0b64_caseD_8007206e;
        case -0x7ff8df91:
          goto switchD_005c0b64_caseD_8007206f;
        case -0x7ff8df90:
          goto switchD_005c0b64_caseD_80072070;
        case -0x7ff8df8f:
          goto switchD_005c0b64_caseD_80072071;
        case -0x7ff8df8e:
          goto switchD_005c0b64_caseD_80072072;
        case -0x7ff8df8d:
          goto switchD_005c0b64_caseD_80072073;
        case -0x7ff8df8c:
          goto switchD_005c0b64_caseD_80072074;
        case -0x7ff8df8b:
          goto switchD_005c0b64_caseD_80072075;
        case -0x7ff8df8a:
          goto switchD_005c0b64_caseD_80072076;
        case -0x7ff8df89:
          goto switchD_005c0b64_caseD_80072077;
        case -0x7ff8df88:
          goto switchD_005c0b64_caseD_80072078;
        case -0x7ff8df87:
          goto switchD_005c0b64_caseD_80072079;
        case -0x7ff8df86:
          goto switchD_005c0b64_caseD_8007207a;
        case -0x7ff8df85:
          goto switchD_005c0b64_caseD_8007207b;
        case -0x7ff8df84:
          goto switchD_005c0b64_caseD_8007207c;
        case -0x7ff8df83:
          goto switchD_005c0b64_caseD_8007207d;
        case -0x7ff8df82:
          goto switchD_005c0b64_caseD_8007207e;
        case -0x7ff8df80:
          goto switchD_005c0b64_caseD_80072080;
        case -0x7ff8df7f:
          goto switchD_005c0b64_caseD_80072081;
        case -0x7ff8df7e:
          goto switchD_005c0b64_caseD_80072082;
        case -0x7ff8df7d:
          goto switchD_005c0b64_caseD_80072083;
        case -0x7ff8df7c:
          goto switchD_005c0b64_caseD_80072084;
        case -0x7ff8df7b:
          goto switchD_005c0b64_caseD_80072085;
        case -0x7ff8df7a:
          goto switchD_005c0b64_caseD_80072086;
        case -0x7ff8df79:
          goto switchD_005c0b64_caseD_80072087;
        case -0x7ff8df78:
          goto switchD_005c0b64_caseD_80072088;
        case -0x7ff8df77:
          goto switchD_005c0b64_caseD_80072089;
        case -0x7ff8df76:
          goto switchD_005c0b64_caseD_8007208a;
        case -0x7ff8df75:
          goto switchD_005c0b64_caseD_8007208b;
        case -0x7ff8df74:
          goto switchD_005c0b64_caseD_8007208c;
        case -0x7ff8df73:
          goto switchD_005c0b64_caseD_8007208d;
        case -0x7ff8df72:
          goto switchD_005c0b64_caseD_8007208e;
        case -0x7ff8df71:
          goto switchD_005c0b64_caseD_8007208f;
        case -0x7ff8df70:
          goto switchD_005c0b64_caseD_80072090;
        case -0x7ff8df6f:
          goto switchD_005c0b64_caseD_80072091;
        case -0x7ff8df6e:
          goto switchD_005c0b64_caseD_80072092;
        case -0x7ff8df6d:
          goto switchD_005c0b64_caseD_80072093;
        case -0x7ff8df6c:
          goto switchD_005c0b64_caseD_80072094;
        case -0x7ff8df6b:
          goto switchD_005c0b64_caseD_80072095;
        case -0x7ff8df6a:
          goto switchD_005c0b64_caseD_80072096;
        case -0x7ff8df69:
          goto switchD_005c0b64_caseD_80072097;
        case -0x7ff8df68:
          goto switchD_005c0b64_caseD_80072098;
        case -0x7ff8df67:
          goto switchD_005c0b64_caseD_80072099;
        case -0x7ff8df66:
          goto switchD_005c0b64_caseD_8007209a;
        case -0x7ff8df65:
          goto switchD_005c0b64_caseD_8007209b;
        case -0x7ff8df64:
          goto switchD_005c0b64_caseD_8007209c;
        case -0x7ff8df63:
          goto switchD_005c0b64_caseD_8007209d;
        case -0x7ff8df62:
          goto switchD_005c0b64_caseD_8007209e;
        case -0x7ff8df61:
          goto switchD_005c0b64_caseD_8007209f;
        case -0x7ff8df60:
          goto switchD_005c0b64_caseD_800720a0;
        case -0x7ff8df5f:
          goto switchD_005c0b64_caseD_800720a1;
        case -0x7ff8df5e:
          goto switchD_005c0b64_caseD_800720a2;
        case -0x7ff8df5d:
          goto switchD_005c0b64_caseD_800720a3;
        case -0x7ff8df5c:
          goto switchD_005c0b64_caseD_800720a4;
        case -0x7ff8df5b:
          goto switchD_005c0b64_caseD_800720a5;
        case -0x7ff8df5a:
          goto switchD_005c0b64_caseD_800720a6;
        case -0x7ff8df59:
          goto switchD_005c0b64_caseD_800720a7;
        case -0x7ff8df58:
          goto switchD_005c0b64_caseD_800720a8;
        case -0x7ff8df57:
          goto switchD_005c0b64_caseD_800720a9;
        case -0x7ff8df56:
          goto switchD_005c0b64_caseD_800720aa;
        case -0x7ff8df55:
          goto switchD_005c0b64_caseD_800720ab;
        case -0x7ff8df54:
          goto switchD_005c0b64_caseD_800720ac;
        case -0x7ff8df53:
          goto switchD_005c0b64_caseD_800720ad;
        case -0x7ff8df52:
          goto switchD_005c0b64_caseD_800720ae;
        case -0x7ff8df51:
          goto switchD_005c0b64_caseD_800720af;
        case -0x7ff8df50:
          goto switchD_005c0b64_caseD_800720b0;
        case -0x7ff8df4f:
          goto switchD_005c0b64_caseD_800720b1;
        case -0x7ff8df4e:
          goto switchD_005c0b64_caseD_800720b2;
        case -0x7ff8df4d:
          goto switchD_005c0b64_caseD_800720b3;
        case -0x7ff8df4c:
          goto switchD_005c0b64_caseD_800720b4;
        case -0x7ff8df4b:
          goto switchD_005c0b64_caseD_800720b5;
        case -0x7ff8df4a:
          goto switchD_005c0b64_caseD_800720b6;
        case -0x7ff8df49:
          goto switchD_005c0b64_caseD_800720b7;
        case -0x7ff8df48:
          goto switchD_005c0b64_caseD_800720b8;
        case -0x7ff8df47:
          goto switchD_005c0b64_caseD_800720b9;
        case -0x7ff8df46:
          goto switchD_005c0b64_caseD_800720ba;
        case -0x7ff8df45:
          goto switchD_005c0b64_caseD_800720bb;
        case -0x7ff8df44:
          goto switchD_005c0b64_caseD_800720bc;
        case -0x7ff8df43:
          goto switchD_005c0b64_caseD_800720bd;
        case -0x7ff8df42:
          goto switchD_005c0b64_caseD_800720be;
        case -0x7ff8df41:
          goto switchD_005c0b64_caseD_800720bf;
        case -0x7ff8df40:
          goto switchD_005c0b64_caseD_800720c0;
        case -0x7ff8df3f:
          goto switchD_005c0b64_caseD_800720c1;
        case -0x7ff8df3e:
          goto switchD_005c0b64_caseD_800720c2;
        case -0x7ff8df3d:
          goto switchD_005c0b64_caseD_800720c3;
        case -0x7ff8df3c:
          goto switchD_005c0b64_caseD_800720c4;
        case -0x7ff8df3b:
          goto switchD_005c0b64_caseD_800720c5;
        case -0x7ff8df3a:
          goto switchD_005c0b64_caseD_800720c6;
        case -0x7ff8df39:
          goto switchD_005c0b64_caseD_800720c7;
        case -0x7ff8df38:
          goto switchD_005c0b64_caseD_800720c8;
        case -0x7ff8df37:
          goto switchD_005c0b64_caseD_800720c9;
        case -0x7ff8df36:
          goto switchD_005c0b64_caseD_800720ca;
        case -0x7ff8df35:
          goto switchD_005c0b64_caseD_800720cb;
        case -0x7ff8df34:
          goto switchD_005c0b64_caseD_800720cc;
        case -0x7ff8df33:
          goto switchD_005c0b64_caseD_800720cd;
        case -0x7ff8df32:
          goto switchD_005c0b64_caseD_800720ce;
        case -0x7ff8df31:
          goto switchD_005c0b64_caseD_800720cf;
        case -0x7ff8df30:
          goto switchD_005c0b64_caseD_800720d0;
        case -0x7ff8df2f:
          goto switchD_005c0b64_caseD_800720d1;
        case -0x7ff8df2e:
          goto switchD_005c0b64_caseD_800720d2;
        case -0x7ff8df2d:
          goto switchD_005c0b64_caseD_800720d3;
        case -0x7ff8df2c:
          goto switchD_005c0b64_caseD_800720d4;
        case -0x7ff8df2b:
          goto switchD_005c0b64_caseD_800720d5;
        case -0x7ff8df2a:
          goto switchD_005c0b64_caseD_800720d6;
        case -0x7ff8df29:
          goto switchD_005c0b64_caseD_800720d7;
        case -0x7ff8df28:
          goto switchD_005c0b64_caseD_800720d8;
        case -0x7ff8df27:
          goto switchD_005c0b64_caseD_800720d9;
        case -0x7ff8df26:
          goto switchD_005c0b64_caseD_800720da;
        case -0x7ff8df25:
          goto switchD_005c0b64_caseD_800720db;
        case -0x7ff8df24:
          goto switchD_005c0b64_caseD_800720dc;
        case -0x7ff8df23:
          goto switchD_005c0b64_caseD_800720dd;
        case -0x7ff8df22:
          goto switchD_005c0b64_caseD_800720de;
        case -0x7ff8df21:
          goto switchD_005c0b64_caseD_800720df;
        case -0x7ff8df20:
          goto switchD_005c0b64_caseD_800720e0;
        case -0x7ff8df1f:
          goto switchD_005c0b64_caseD_800720e1;
        case -0x7ff8df1e:
          goto switchD_005c0b64_caseD_800720e2;
        case -0x7ff8df1d:
          goto switchD_005c0b64_caseD_800720e3;
        case -0x7ff8df1c:
          goto switchD_005c0b64_caseD_800720e4;
        case -0x7ff8df1b:
          goto switchD_005c0b64_caseD_800720e5;
        case -0x7ff8df1a:
          goto switchD_005c0b64_caseD_800720e6;
        case -0x7ff8df19:
          goto switchD_005c0b64_caseD_800720e7;
        case -0x7ff8df18:
          goto switchD_005c0b64_caseD_800720e8;
        case -0x7ff8df17:
          goto switchD_005c0b64_caseD_800720e9;
        case -0x7ff8df16:
          goto switchD_005c0b64_caseD_800720ea;
        case -0x7ff8df15:
          goto switchD_005c0b64_caseD_800720eb;
        case -0x7ff8df14:
          goto switchD_005c0b64_caseD_800720ec;
        case -0x7ff8df13:
          goto switchD_005c0b64_caseD_800720ed;
        case -0x7ff8df12:
          goto switchD_005c0b64_caseD_800720ee;
        case -0x7ff8df11:
          goto switchD_005c0b64_caseD_800720ef;
        case -0x7ff8df10:
          goto switchD_005c0b64_caseD_800720f0;
        case -0x7ff8df0f:
          goto switchD_005c0b64_caseD_800720f1;
        case -0x7ff8df0e:
          goto switchD_005c0b64_caseD_800720f2;
        case -0x7ff8df0d:
          goto switchD_005c0b64_caseD_800720f3;
        case -0x7ff8df0c:
          goto switchD_005c0b64_caseD_800720f4;
        case -0x7ff8df0b:
          goto switchD_005c0b64_caseD_800720f5;
        case -0x7ff8df0a:
          goto switchD_005c0b64_caseD_800720f6;
        case -0x7ff8df09:
          goto switchD_005c0b64_caseD_800720f7;
        case -0x7ff8df08:
          goto switchD_005c0b64_caseD_800720f8;
        case -0x7ff8df07:
          goto switchD_005c0b64_caseD_800720f9;
        case -0x7ff8df06:
          goto switchD_005c0b64_caseD_800720fa;
        case -0x7ff8df05:
          goto switchD_005c0b64_caseD_800720fb;
        case -0x7ff8df04:
          goto switchD_005c0b64_caseD_800720fc;
        case -0x7ff8df03:
          goto switchD_005c0b64_caseD_800720fd;
        case -0x7ff8df02:
          goto switchD_005c0b64_caseD_800720fe;
        case -0x7ff8df01:
          goto switchD_005c0b64_caseD_800720ff;
        case -0x7ff8df00:
          goto switchD_005c0b64_caseD_80072100;
        case -0x7ff8deff:
          goto switchD_005c0b64_caseD_80072101;
        case -0x7ff8defe:
          goto switchD_005c0b64_caseD_80072102;
        case -0x7ff8defd:
          goto switchD_005c0b64_caseD_80072103;
        case -0x7ff8defc:
          goto switchD_005c0b64_caseD_80072104;
        case -0x7ff8defb:
          goto switchD_005c0b64_caseD_80072105;
        case -0x7ff8defa:
          goto switchD_005c0b64_caseD_80072106;
        case -0x7ff8def9:
          goto switchD_005c0b64_caseD_80072107;
        case -0x7ff8def8:
          goto switchD_005c0b64_caseD_80072108;
        case -0x7ff8def7:
          goto switchD_005c0b64_caseD_80072109;
        case -0x7ff8def6:
          goto switchD_005c0b64_caseD_8007210a;
        case -0x7ff8def5:
          goto switchD_005c0b64_caseD_8007210b;
        case -0x7ff8def4:
          goto switchD_005c0b64_caseD_8007210c;
        case -0x7ff8def3:
          goto switchD_005c0b64_caseD_8007210d;
        case -0x7ff8def2:
          goto switchD_005c0b64_caseD_8007210e;
        case -0x7ff8def1:
          goto switchD_005c0b64_caseD_8007210f;
        case -0x7ff8def0:
          goto switchD_005c0b64_caseD_80072110;
        case -0x7ff8deef:
          goto switchD_005c0b64_caseD_80072111;
        case -0x7ff8deee:
          goto switchD_005c0b64_caseD_80072112;
        case -0x7ff8deed:
          goto switchD_005c0b64_caseD_80072113;
        case -0x7ff8deec:
          goto switchD_005c0b64_caseD_80072114;
        case -0x7ff8deeb:
          goto switchD_005c0b64_caseD_80072115;
        case -0x7ff8deea:
          goto switchD_005c0b64_caseD_80072116;
        case -0x7ff8dee9:
          goto switchD_005c0b64_caseD_80072117;
        case -0x7ff8dee8:
          goto switchD_005c0b64_caseD_80072118;
        case -0x7ff8dee7:
          goto switchD_005c0b64_caseD_80072119;
        case -0x7ff8dee6:
          goto switchD_005c0b64_caseD_8007211a;
        case -0x7ff8dee5:
          goto switchD_005c0b64_caseD_8007211b;
        case -0x7ff8dee4:
          goto switchD_005c0b64_caseD_8007211c;
        case -0x7ff8dee3:
          goto switchD_005c0b64_caseD_8007211d;
        case -0x7ff8dee2:
          goto switchD_005c0b64_caseD_8007211e;
        case -0x7ff8dee1:
          goto switchD_005c0b64_caseD_8007211f;
        case -0x7ff8dee0:
          goto switchD_005c0b64_caseD_80072120;
        case -0x7ff8dedf:
          goto switchD_005c0b64_caseD_80072121;
        case -0x7ff8dede:
          goto switchD_005c0b64_caseD_80072122;
        case -0x7ff8dedd:
          goto switchD_005c0b64_caseD_80072123;
        case -0x7ff8dedc:
          goto switchD_005c0b64_caseD_80072124;
        case -0x7ff8dedb:
          goto switchD_005c0b64_caseD_80072125;
        case -0x7ff8deda:
          goto switchD_005c0b64_caseD_80072126;
        case -0x7ff8ded9:
          goto switchD_005c0b64_caseD_80072127;
        case -0x7ff8ded8:
          goto switchD_005c0b64_caseD_80072128;
        case -0x7ff8ded7:
          goto switchD_005c0b64_caseD_80072129;
        case -0x7ff8ded6:
          goto switchD_005c0b64_caseD_8007212a;
        case -0x7ff8ded5:
          goto switchD_005c0b64_caseD_8007212b;
        case -0x7ff8ded4:
          goto switchD_005c0b64_caseD_8007212c;
        case -0x7ff8ded3:
          goto switchD_005c0b64_caseD_8007212d;
        case -0x7ff8ded2:
          goto switchD_005c0b64_caseD_8007212e;
        case -0x7ff8ded1:
          goto switchD_005c0b64_caseD_8007212f;
        case -0x7ff8ded0:
          goto switchD_005c0b64_caseD_80072130;
        case -0x7ff8decf:
          goto switchD_005c0b64_caseD_80072131;
        case -0x7ff8dece:
          goto switchD_005c0b64_caseD_80072132;
        case -0x7ff8decd:
          goto switchD_005c0b64_caseD_80072133;
        case -0x7ff8decc:
          goto switchD_005c0b64_caseD_80072134;
        case -0x7ff8decb:
          goto switchD_005c0b64_caseD_80072135;
        case -0x7ff8deca:
          goto switchD_005c0b64_caseD_80072136;
        case -0x7ff8dec9:
          goto switchD_005c0b64_caseD_80072137;
        case -0x7ff8dec8:
          goto switchD_005c0b64_caseD_80072138;
        case -0x7ff8dec7:
          goto switchD_005c0b64_caseD_80072139;
        case -0x7ff8dec6:
          goto switchD_005c0b64_caseD_8007213a;
        case -0x7ff8dec5:
          goto switchD_005c0b64_caseD_8007213b;
        case -0x7ff8dec4:
          goto switchD_005c0b64_caseD_8007213c;
        case -0x7ff8dec3:
          goto switchD_005c0b64_caseD_8007213d;
        case -0x7ff8dec2:
          goto switchD_005c0b64_caseD_8007213e;
        case -0x7ff8dec1:
          goto switchD_005c0b64_caseD_8007213f;
        case -0x7ff8dec0:
          goto switchD_005c0b64_caseD_80072140;
        case -0x7ff8debf:
          goto switchD_005c0b64_caseD_80072141;
        case -0x7ff8debe:
          goto switchD_005c0b64_caseD_80072142;
        case -0x7ff8debd:
          goto switchD_005c0b64_caseD_80072143;
        case -0x7ff8debc:
          goto switchD_005c0b64_caseD_80072144;
        case -0x7ff8debb:
          goto switchD_005c0b64_caseD_80072145;
        case -0x7ff8deba:
          goto switchD_005c0b64_caseD_80072146;
        case -0x7ff8deb9:
          goto switchD_005c0b64_caseD_80072147;
        case -0x7ff8deb8:
          goto switchD_005c0b64_caseD_80072148;
        case -0x7ff8deb7:
          goto switchD_005c0b64_caseD_80072149;
        case -0x7ff8deb6:
          goto switchD_005c0b64_caseD_8007214a;
        case -0x7ff8deb5:
          goto switchD_005c0b64_caseD_8007214b;
        case -0x7ff8deb4:
          goto switchD_005c0b64_caseD_8007214c;
        case -0x7ff8deb3:
          goto switchD_005c0b64_caseD_8007214d;
        case -0x7ff8deb2:
          goto switchD_005c0b64_caseD_8007214e;
        case -0x7ff8deb1:
          goto switchD_005c0b64_caseD_8007214f;
        case -0x7ff8deb0:
          goto switchD_005c0b64_caseD_80072150;
        case -0x7ff8deaf:
          goto switchD_005c0b64_caseD_80072151;
        case -0x7ff8deae:
          goto switchD_005c0b64_caseD_80072152;
        case -0x7ff8dead:
          goto switchD_005c0b64_caseD_80072153;
        case -0x7ff8deac:
          goto switchD_005c0b64_caseD_80072154;
        case -0x7ff8deab:
          goto switchD_005c0b64_caseD_80072155;
        case -0x7ff8deaa:
          goto switchD_005c0b64_caseD_80072156;
        case -0x7ff8dea9:
          goto switchD_005c0b64_caseD_80072157;
        case -0x7ff8dea8:
          goto switchD_005c0b64_caseD_80072158;
        case -0x7ff8dea7:
          goto switchD_005c0b64_caseD_80072159;
        case -0x7ff8dea6:
          goto switchD_005c0b64_caseD_8007215a;
        case -0x7ff8dea5:
          goto switchD_005c0b64_caseD_8007215b;
        case -0x7ff8dea4:
          goto switchD_005c0b64_caseD_8007215c;
        case -0x7ff8dea3:
          goto switchD_005c0b64_caseD_8007215d;
        case -0x7ff8dea2:
          goto switchD_005c0b64_caseD_8007215e;
        case -0x7ff8dea1:
          goto switchD_005c0b64_caseD_8007215f;
        case -0x7ff8dea0:
          goto switchD_005c0b64_caseD_80072160;
        case -0x7ff8de9f:
          goto switchD_005c0b64_caseD_80072161;
        case -0x7ff8de9e:
          goto switchD_005c0b64_caseD_80072162;
        case -0x7ff8de9d:
          goto switchD_005c0b64_caseD_80072163;
        case -0x7ff8de9c:
          goto switchD_005c0b64_caseD_80072164;
        case -0x7ff8de9b:
          goto switchD_005c0b64_caseD_80072165;
        case -0x7ff8de9a:
          goto switchD_005c0b64_caseD_80072166;
        case -0x7ff8de99:
          goto switchD_005c0b64_caseD_80072167;
        case -0x7ff8de98:
          goto switchD_005c0b64_caseD_80072168;
        case -0x7ff8de97:
          goto switchD_005c0b64_caseD_80072169;
        case -0x7ff8de96:
          goto switchD_005c0b64_caseD_8007216a;
        case -0x7ff8de95:
          goto switchD_005c0b64_caseD_8007216b;
        case -0x7ff8de94:
          goto switchD_005c0b64_caseD_8007216c;
        case -0x7ff8de93:
          goto switchD_005c0b64_caseD_8007216d;
        case -0x7ff8de92:
          goto switchD_005c0b64_caseD_8007216e;
        case -0x7ff8de91:
          goto switchD_005c0b64_caseD_8007216f;
        case -0x7ff8de90:
          goto switchD_005c0b64_caseD_80072170;
        case -0x7ff8de8f:
          goto switchD_005c0b64_caseD_80072171;
        case -0x7ff8de8e:
          goto switchD_005c0b64_caseD_80072172;
        case -0x7ff8de8d:
          goto switchD_005c0b64_caseD_80072173;
        case -0x7ff8de8c:
          goto switchD_005c0b64_caseD_80072174;
        case -0x7ff8de8b:
          goto switchD_005c0b64_caseD_80072175;
        case -0x7ff8de8a:
          goto switchD_005c0b64_caseD_80072176;
        case -0x7ff8de89:
          goto switchD_005c0b64_caseD_80072177;
        case -0x7ff8de88:
          goto switchD_005c0b64_caseD_80072178;
        case -0x7ff8de87:
          goto switchD_005c0b64_caseD_80072179;
        case -0x7ff8de86:
          goto switchD_005c0b64_caseD_8007217a;
        case -0x7ff8de85:
          goto switchD_005c0b64_caseD_8007217b;
        case -0x7ff8de84:
          goto switchD_005c0b64_caseD_8007217c;
        case -0x7ff8de83:
          goto switchD_005c0b64_caseD_8007217d;
        case -0x7ff8de82:
          goto switchD_005c0b64_caseD_8007217e;
        case -0x7ff8de81:
          goto switchD_005c0b64_caseD_8007217f;
        case -0x7ff8de80:
          goto switchD_005c0b64_caseD_80072180;
        case -0x7ff8de7f:
          goto switchD_005c0b64_caseD_80072181;
        case -0x7ff8de7e:
          goto switchD_005c0b64_caseD_80072182;
        case -0x7ff8de7d:
          goto switchD_005c0b64_caseD_80072183;
        case -0x7ff8de7c:
          goto switchD_005c0b64_caseD_80072184;
        case -0x7ff8de7b:
          goto switchD_005c0b64_caseD_80072185;
        case -0x7ff8de7a:
          goto switchD_005c0b64_caseD_80072186;
        case -0x7ff8de79:
          goto switchD_005c0b64_caseD_80072187;
        case -0x7ff8de78:
          goto switchD_005c0b64_caseD_80072188;
        case -0x7ff8de77:
          goto switchD_005c0b64_caseD_80072189;
        case -0x7ff8de76:
          goto switchD_005c0b64_caseD_8007218a;
        case -0x7ff8de75:
          goto switchD_005c0b64_caseD_8007218b;
        case -0x7ff8de74:
          goto switchD_005c0b64_caseD_8007218c;
        case -0x7ff8de73:
          goto switchD_005c0b64_caseD_8007218d;
        case -0x7ff8de72:
          goto switchD_005c0b64_caseD_8007218e;
        case -0x7ff8de71:
          goto switchD_005c0b64_caseD_8007218f;
        case -0x7ff8de70:
          goto switchD_005c0b64_caseD_80072190;
        case -0x7ff8de6f:
          goto switchD_005c0b64_caseD_80072191;
        case -0x7ff8de6e:
          goto switchD_005c0b64_caseD_80072192;
        case -0x7ff8de6d:
          goto switchD_005c0b64_caseD_80072193;
        case -0x7ff8de6c:
          goto switchD_005c0b64_caseD_80072194;
        case -0x7ff8de6b:
          goto switchD_005c0b64_caseD_80072195;
        case -0x7ff8de6a:
          goto switchD_005c0b64_caseD_80072196;
        case -0x7ff8de69:
          goto switchD_005c0b64_caseD_80072197;
        case -0x7ff8de68:
          goto switchD_005c0b64_caseD_80072198;
        case -0x7ff8de67:
          goto switchD_005c0b64_caseD_80072199;
        case -0x7ff8de66:
          goto switchD_005c0b64_caseD_8007219a;
        case -0x7ff8de65:
          goto switchD_005c0b64_caseD_8007219b;
        case -0x7ff8de64:
          goto switchD_005c0b64_caseD_8007219c;
        case -0x7ff8de63:
          goto switchD_005c0b64_caseD_8007219d;
        case -0x7ff8de62:
          goto switchD_005c0b64_caseD_8007219e;
        case -0x7ff8de61:
          goto switchD_005c0b64_caseD_8007219f;
        case -0x7ff8de60:
          goto switchD_005c0b64_caseD_800721a0;
        case -0x7ff8de5f:
          goto switchD_005c0b64_caseD_800721a1;
        case -0x7ff8de5e:
          goto switchD_005c0b64_caseD_800721a2;
        }
      }
    }
    else if (in_stack_00000004 < -0x7ff8c938) {
      if (in_stack_00000004 == -0x7ff8c939) {
switchD_005c91b2_caseD_36c7:
        return (int)"ERROR_SXS_DUPLICATE_CLSID";
      }
      if (in_stack_00000004 < -0x7ff8d505) {
        if (in_stack_00000004 == -0x7ff8d506) {
LAB_005c8b23:
          return (int)"WSATRY_AGAIN";
        }
        if (in_stack_00000004 < -0x7ff8da0d) {
          if (in_stack_00000004 == -0x7ff8da0e) goto switchD_005c8591_caseD_25f2;
          if (in_stack_00000004 < -0x7ff8da7d) {
            if (in_stack_00000004 == -0x7ff8da7e) goto switchD_005c8591_caseD_2582;
            if (in_stack_00000004 < -0x7ff8dadf) {
              if (in_stack_00000004 == -0x7ff8dae0) goto switchD_005c8591_caseD_2520;
              if (in_stack_00000004 < -0x7ff8dccf) {
                if (in_stack_00000004 == -0x7ff8dcd0) goto switchD_005c84df_caseD_2330;
                if (in_stack_00000004 < -0x7ff8dcd4) {
                  if (in_stack_00000004 == -0x7ff8dcd5) goto switchD_005c84df_caseD_232b;
                  if (in_stack_00000004 == -0x7ff8de5c) goto switchD_005c81e1_caseD_21a4;
                  if (in_stack_00000004 == -0x7ff8de5b) goto switchD_005c81e1_caseD_21a5;
                  if (in_stack_00000004 == -0x7ff8dcd8) goto LAB_005c84b8;
                  if (in_stack_00000004 == -0x7ff8dcd7) goto switchD_005c84df_caseD_2329;
                  if (in_stack_00000004 == -0x7ff8dcd6) goto switchD_005c84df_caseD_232a;
                }
                else {
                  if (in_stack_00000004 == -0x7ff8dcd4) goto switchD_005c84df_caseD_232c;
                  if (in_stack_00000004 == -0x7ff8dcd3) goto switchD_005c84df_caseD_232d;
                  if (in_stack_00000004 == -0x7ff8dcd2) goto switchD_005c84df_caseD_232e;
                  if (in_stack_00000004 == -0x7ff8dcd1) goto switchD_005c84df_caseD_232f;
                }
              }
              else if (in_stack_00000004 < -0x7ff8dcc5) {
                if (in_stack_00000004 == -0x7ff8dcc6) goto switchD_005c84df_caseD_233a;
                if (in_stack_00000004 == -0x7ff8dccf) goto switchD_005c84df_caseD_2331;
                if (in_stack_00000004 == -0x7ff8dcce) goto switchD_005c84df_caseD_2332;
                if (in_stack_00000004 == -0x7ff8dcc8) goto switchD_005c84df_caseD_2338;
                if (in_stack_00000004 == -0x7ff8dcc7) goto switchD_005c84df_caseD_2339;
              }
              else {
                if (in_stack_00000004 == -0x7ff8dae4) goto LAB_005c854a;
                if (in_stack_00000004 == -0x7ff8dae3) goto switchD_005c8591_caseD_251d;
                if (in_stack_00000004 == -0x7ff8dae2) goto switchD_005c8591_caseD_251e;
                if (in_stack_00000004 == -0x7ff8dae1) goto switchD_005c8591_caseD_251f;
              }
            }
            else if (in_stack_00000004 < -0x7ff8daa9) {
              if (in_stack_00000004 == -0x7ff8daaa) goto switchD_005c8591_caseD_2556;
              if (in_stack_00000004 < -0x7ff8daae) {
                if (in_stack_00000004 == -0x7ff8daaf) goto switchD_005c8591_caseD_2551;
                if (in_stack_00000004 == -0x7ff8dadf) goto switchD_005c8591_caseD_2521;
                if (in_stack_00000004 == -0x7ff8dab2) goto switchD_005c8591_caseD_254e;
                if (in_stack_00000004 == -0x7ff8dab1) goto switchD_005c8591_caseD_254f;
                if (in_stack_00000004 == -0x7ff8dab0) goto switchD_005c8591_caseD_2550;
              }
              else {
                if (in_stack_00000004 == -0x7ff8daae) goto switchD_005c8591_caseD_2552;
                if (in_stack_00000004 == -0x7ff8daad) goto switchD_005c8591_caseD_2553;
                if (in_stack_00000004 == -0x7ff8daac) goto switchD_005c8591_caseD_2554;
                if (in_stack_00000004 == -0x7ff8daab) goto switchD_005c8591_caseD_2555;
              }
            }
            else if (in_stack_00000004 < -0x7ff8daa4) {
              if (in_stack_00000004 == -0x7ff8daa5) goto switchD_005c8591_caseD_255b;
              if (in_stack_00000004 == -0x7ff8daa9) goto switchD_005c8591_caseD_2557;
              if (in_stack_00000004 == -0x7ff8daa8) goto switchD_005c8591_caseD_2558;
              if (in_stack_00000004 == -0x7ff8daa7) goto switchD_005c8591_caseD_2559;
              if (in_stack_00000004 == -0x7ff8daa6) goto switchD_005c8591_caseD_255a;
            }
            else {
              if (in_stack_00000004 == -0x7ff8daa4) goto switchD_005c8591_caseD_255c;
              if (in_stack_00000004 == -0x7ff8daa3) goto switchD_005c8591_caseD_255d;
              if (in_stack_00000004 == -0x7ff8da80) goto switchD_005c8591_caseD_2580;
              if (in_stack_00000004 == -0x7ff8da7f) goto switchD_005c8591_caseD_2581;
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7ff8da7d:
              goto switchD_005c0df2_caseD_80072583;
            case -0x7ff8da7c:
              goto switchD_005c0df2_caseD_80072584;
            case -0x7ff8da7b:
              goto switchD_005c0df2_caseD_80072585;
            case -0x7ff8da7a:
              goto switchD_005c0df2_caseD_80072586;
            case -0x7ff8da79:
              goto switchD_005c0df2_caseD_80072587;
            case -0x7ff8da78:
              goto switchD_005c0df2_caseD_80072588;
            case -0x7ff8da77:
              goto switchD_005c0df2_caseD_80072589;
            case -0x7ff8da76:
              goto switchD_005c0df2_caseD_8007258a;
            case -0x7ff8da75:
              goto switchD_005c0df2_caseD_8007258b;
            case -0x7ff8da74:
              goto switchD_005c0df2_caseD_8007258c;
            case -0x7ff8da73:
              goto switchD_005c0df2_caseD_8007258d;
            case -0x7ff8da72:
              goto switchD_005c0df2_caseD_8007258e;
            case -0x7ff8da71:
              goto switchD_005c0df2_caseD_8007258f;
            case -0x7ff8da70:
              goto switchD_005c0df2_caseD_80072590;
            case -0x7ff8da6f:
              goto switchD_005c0df2_caseD_80072591;
            case -0x7ff8da6e:
              goto switchD_005c0df2_caseD_80072592;
            case -0x7ff8da6d:
              goto switchD_005c0df2_caseD_80072593;
            case -0x7ff8da6c:
              goto switchD_005c0df2_caseD_80072594;
            case -0x7ff8da6b:
              goto switchD_005c0df2_caseD_80072595;
            case -0x7ff8da4e:
              goto switchD_005c0df2_caseD_800725b2;
            case -0x7ff8da4d:
              goto switchD_005c0df2_caseD_800725b3;
            case -0x7ff8da4c:
              goto switchD_005c0df2_caseD_800725b4;
            case -0x7ff8da4b:
              goto switchD_005c0df2_caseD_800725b5;
            case -0x7ff8da4a:
              goto switchD_005c0df2_caseD_800725b6;
            case -0x7ff8da49:
              goto switchD_005c0df2_caseD_800725b7;
            case -0x7ff8da1c:
              goto switchD_005c0df2_caseD_800725e4;
            case -0x7ff8da1b:
              goto switchD_005c0df2_caseD_800725e5;
            case -0x7ff8da1a:
              goto switchD_005c0df2_caseD_800725e6;
            case -0x7ff8da19:
              goto switchD_005c0df2_caseD_800725e7;
            case -0x7ff8da18:
              goto switchD_005c0df2_caseD_800725e8;
            case -0x7ff8da17:
              goto switchD_005c0df2_caseD_800725e9;
            case -0x7ff8da16:
              goto switchD_005c0df2_caseD_800725ea;
            case -0x7ff8da15:
              goto switchD_005c0df2_caseD_800725eb;
            case -0x7ff8da14:
              goto switchD_005c0df2_caseD_800725ec;
            case -0x7ff8da13:
              goto switchD_005c0df2_caseD_800725ed;
            case -0x7ff8da12:
              goto switchD_005c0df2_caseD_800725ee;
            case -0x7ff8da11:
              goto switchD_005c0df2_caseD_800725ef;
            case -0x7ff8da10:
              goto switchD_005c0df2_caseD_800725f0;
            case -0x7ff8da0f:
              goto switchD_005c0df2_caseD_800725f1;
            }
          }
        }
        else if (in_stack_00000004 < -0x7ff8d8bf) {
          if (in_stack_00000004 == -0x7ff8d8c0) goto switchD_005c8591_caseD_2740;
          if (in_stack_00000004 < -0x7ff8d8ef) {
            if (in_stack_00000004 == -0x7ff8d8f0) goto switchD_005c8591_caseD_2710;
            if (in_stack_00000004 < -0x7ff8d9b6) {
              if (in_stack_00000004 == -0x7ff8d9b7) goto switchD_005c8591_caseD_2649;
              if (in_stack_00000004 < -0x7ff8d9e9) {
                if (in_stack_00000004 == -0x7ff8d9ea) goto switchD_005c8591_caseD_2616;
                if (in_stack_00000004 == -0x7ff8da0d) goto switchD_005c8591_caseD_25f3;
                if (in_stack_00000004 == -0x7ff8da0c) goto switchD_005c8591_caseD_25f4;
                if (in_stack_00000004 == -0x7ff8da0b) goto switchD_005c8591_caseD_25f5;
                if (in_stack_00000004 == -0x7ff8da0a) goto switchD_005c8591_caseD_25f6;
                if (in_stack_00000004 == -0x7ff8da09) goto switchD_005c8591_caseD_25f7;
              }
              else {
                if (in_stack_00000004 == -0x7ff8d9e9) goto switchD_005c8591_caseD_2617;
                if (in_stack_00000004 == -0x7ff8d9e8) goto switchD_005c8591_caseD_2618;
                if (in_stack_00000004 == -0x7ff8d9e7) goto switchD_005c8591_caseD_2619;
                if (in_stack_00000004 == -0x7ff8d9b8) goto switchD_005c8591_caseD_2648;
              }
            }
            else if (in_stack_00000004 < -0x7ff8d952) {
              if (in_stack_00000004 == -0x7ff8d953) goto switchD_005c8591_caseD_26ad;
              if (in_stack_00000004 == -0x7ff8d986) goto switchD_005c8591_caseD_267a;
              if (in_stack_00000004 == -0x7ff8d985) goto switchD_005c8591_caseD_267b;
              if (in_stack_00000004 == -0x7ff8d984) goto switchD_005c8591_caseD_267c;
              if (in_stack_00000004 == -0x7ff8d954) goto switchD_005c8591_caseD_26ac;
            }
            else {
              if (in_stack_00000004 == -0x7ff8d952) goto switchD_005c8591_caseD_26ae;
              if (in_stack_00000004 == -0x7ff8d951) goto switchD_005c8591_caseD_26af;
              if (in_stack_00000004 == -0x7ff8d950) goto switchD_005c8591_caseD_26b0;
              if (in_stack_00000004 == -0x7ff8d94f) goto switchD_005c8591_caseD_26b1;
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7ff8d8ec:
              goto switchD_005c0f44_caseD_80072714;
            case -0x7ff8d8e7:
              goto switchD_005c0f44_caseD_80072719;
            case -0x7ff8d8e3:
              goto switchD_005c0f44_caseD_8007271d;
            case -0x7ff8d8e2:
              goto switchD_005c0f44_caseD_8007271e;
            case -0x7ff8d8da:
              goto switchD_005c0f44_caseD_80072726;
            case -0x7ff8d8d8:
              goto switchD_005c0f44_caseD_80072728;
            case -0x7ff8d8cd:
              goto switchD_005c0f44_caseD_80072733;
            case -0x7ff8d8cc:
              goto switchD_005c0f44_caseD_80072734;
            case -0x7ff8d8cb:
              goto switchD_005c0f44_caseD_80072735;
            case -0x7ff8d8ca:
              goto switchD_005c0f44_caseD_80072736;
            case -0x7ff8d8c9:
              goto switchD_005c0f44_caseD_80072737;
            case -0x7ff8d8c8:
              goto switchD_005c0f44_caseD_80072738;
            case -0x7ff8d8c7:
              goto switchD_005c0f44_caseD_80072739;
            case -0x7ff8d8c6:
              goto switchD_005c0f44_caseD_8007273a;
            case -0x7ff8d8c5:
              goto switchD_005c0f44_caseD_8007273b;
            case -0x7ff8d8c4:
              goto switchD_005c0f44_caseD_8007273c;
            case -0x7ff8d8c3:
              goto switchD_005c0f44_caseD_8007273d;
            case -0x7ff8d8c2:
              goto switchD_005c0f44_caseD_8007273e;
            case -0x7ff8d8c1:
              goto switchD_005c0f44_caseD_8007273f;
            }
          }
        }
        else if (in_stack_00000004 < -0x7ff8d506) {
          if (in_stack_00000004 == -0x7ff8d507) {
LAB_005c8b2d:
            return (int)"WSAHOST_NOT_FOUND";
          }
          switch(in_stack_00000004) {
          case -0x7ff8d8bf:
            goto switchD_005c0f73_caseD_80072741;
          case -0x7ff8d8be:
            goto switchD_005c0f73_caseD_80072742;
          case -0x7ff8d8bd:
            goto switchD_005c0f73_caseD_80072743;
          case -0x7ff8d8bc:
            goto switchD_005c0f73_caseD_80072744;
          case -0x7ff8d8bb:
            goto switchD_005c0f73_caseD_80072745;
          case -0x7ff8d8ba:
            goto switchD_005c0f73_caseD_80072746;
          case -0x7ff8d8b9:
            goto switchD_005c0f73_caseD_80072747;
          case -0x7ff8d8b8:
            goto switchD_005c0f73_caseD_80072748;
          case -0x7ff8d8b7:
            goto switchD_005c0f73_caseD_80072749;
          case -0x7ff8d8b6:
            goto switchD_005c0f73_caseD_8007274a;
          case -0x7ff8d8b5:
            goto switchD_005c0f73_caseD_8007274b;
          case -0x7ff8d8b4:
            goto switchD_005c0f73_caseD_8007274c;
          case -0x7ff8d8b3:
            goto switchD_005c0f73_caseD_8007274d;
          case -0x7ff8d8b2:
            goto switchD_005c0f73_caseD_8007274e;
          case -0x7ff8d8b1:
            goto switchD_005c0f73_caseD_8007274f;
          case -0x7ff8d8b0:
            goto switchD_005c0f73_caseD_80072750;
          case -0x7ff8d8af:
            goto switchD_005c0f73_caseD_80072751;
          case -0x7ff8d8ae:
switchD_005c0f73_caseD_80072752:
            return (int)"WSAENOTEMPTY";
          case -0x7ff8d8ad:
switchD_005c0f73_caseD_80072753:
            return (int)"WSAEPROCLIM";
          case -0x7ff8d8ac:
switchD_005c0f73_caseD_80072754:
            return (int)"WSAEUSERS";
          case -0x7ff8d8ab:
switchD_005c0f73_caseD_80072755:
            return (int)"WSAEDQUOT";
          case -0x7ff8d8aa:
switchD_005c0f73_caseD_80072756:
            return (int)"WSAESTALE";
          case -0x7ff8d8a9:
switchD_005c0f73_caseD_80072757:
            return (int)"WSAEREMOTE";
          case -0x7ff8d895:
switchD_005c0f73_caseD_8007276b:
            return (int)"WSASYSNOTREADY";
          case -0x7ff8d894:
switchD_005c0f73_caseD_8007276c:
            return (int)"WSAVERNOTSUPPORTED";
          case -0x7ff8d893:
switchD_005c0f73_caseD_8007276d:
            return (int)"WSANOTINITIALISED";
          case -0x7ff8d88b:
switchD_005c0f73_caseD_80072775:
            return (int)"WSAEDISCON";
          case -0x7ff8d88a:
switchD_005c0f73_caseD_80072776:
            return (int)"WSAENOMORE";
          case -0x7ff8d889:
switchD_005c0f73_caseD_80072777:
            return (int)"WSAECANCELLED";
          case -0x7ff8d888:
switchD_005c0f73_caseD_80072778:
            return (int)"WSAEINVALIDPROCTABLE";
          case -0x7ff8d887:
switchD_005c0f73_caseD_80072779:
            return (int)"WSAEINVALIDPROVIDER";
          case -0x7ff8d886:
switchD_005c0f73_caseD_8007277a:
            return (int)"WSAEPROVIDERFAILEDINIT";
          case -0x7ff8d885:
switchD_005c0f73_caseD_8007277b:
            return (int)"WSASYSCALLFAILURE";
          case -0x7ff8d884:
switchD_005c0f73_caseD_8007277c:
            return (int)"WSASERVICE_NOT_FOUND";
          case -0x7ff8d883:
switchD_005c0f73_caseD_8007277d:
            return (int)"WSATYPE_NOT_FOUND";
          case -0x7ff8d882:
switchD_005c0f73_caseD_8007277e:
            return (int)"WSA_E_NO_MORE";
          case -0x7ff8d881:
switchD_005c0f73_caseD_8007277f:
            return (int)"WSA_E_CANCELLED";
          case -0x7ff8d880:
switchD_005c0f73_caseD_80072780:
            return (int)"WSAEREFUSED";
          }
        }
      }
      else if (in_stack_00000004 < -0x7ff8cd37) {
        if (in_stack_00000004 == -0x7ff8cd38) {
LAB_005c8ccd:
          return (int)"ERROR_IPSEC_QM_POLICY_EXISTS";
        }
        switch(in_stack_00000004) {
        case -0x7ff8d505:
switchD_005c0f97_caseD_80072afb:
          return (int)"WSANO_RECOVERY";
        case -0x7ff8d504:
switchD_005c0f97_caseD_80072afc:
          return (int)"WSANO_DATA";
        case -0x7ff8d503:
switchD_005c0f97_caseD_80072afd:
          return (int)"WSA_QOS_RECEIVERS";
        case -0x7ff8d502:
switchD_005c0f97_caseD_80072afe:
          return (int)"WSA_QOS_SENDERS";
        case -0x7ff8d501:
switchD_005c0f97_caseD_80072aff:
          return (int)"WSA_QOS_NO_SENDERS";
        case -0x7ff8d500:
switchD_005c0f97_caseD_80072b00:
          return (int)"WSA_QOS_NO_RECEIVERS";
        case -0x7ff8d4ff:
switchD_005c0f97_caseD_80072b01:
          return (int)"WSA_QOS_REQUEST_CONFIRMED";
        case -0x7ff8d4fe:
switchD_005c0f97_caseD_80072b02:
          return (int)"WSA_QOS_ADMISSION_FAILURE";
        case -0x7ff8d4fd:
switchD_005c0f97_caseD_80072b03:
          return (int)"WSA_QOS_POLICY_FAILURE";
        case -0x7ff8d4fc:
switchD_005c0f97_caseD_80072b04:
          return (int)"WSA_QOS_BAD_STYLE";
        case -0x7ff8d4fb:
switchD_005c0f97_caseD_80072b05:
          return (int)"WSA_QOS_BAD_OBJECT";
        case -0x7ff8d4fa:
switchD_005c0f97_caseD_80072b06:
          return (int)"WSA_QOS_TRAFFIC_CTRL_ERROR";
        case -0x7ff8d4f9:
switchD_005c0f97_caseD_80072b07:
          return (int)"WSA_QOS_GENERIC_ERROR";
        case -0x7ff8d4f8:
switchD_005c0f97_caseD_80072b08:
          return (int)"WSA_QOS_ESERVICETYPE";
        case -0x7ff8d4f7:
switchD_005c0f97_caseD_80072b09:
          return (int)"WSA_QOS_EFLOWSPEC";
        case -0x7ff8d4f6:
switchD_005c0f97_caseD_80072b0a:
          return (int)"WSA_QOS_EPROVSPECBUF";
        case -0x7ff8d4f5:
switchD_005c0f97_caseD_80072b0b:
          return (int)"WSA_QOS_EFILTERSTYLE";
        case -0x7ff8d4f4:
switchD_005c0f97_caseD_80072b0c:
          return (int)"WSA_QOS_EFILTERTYPE";
        case -0x7ff8d4f3:
switchD_005c0f97_caseD_80072b0d:
          return (int)"WSA_QOS_EFILTERCOUNT";
        case -0x7ff8d4f2:
switchD_005c0f97_caseD_80072b0e:
          return (int)"WSA_QOS_EOBJLENGTH";
        case -0x7ff8d4f1:
switchD_005c0f97_caseD_80072b0f:
          return (int)"WSA_QOS_EFLOWCOUNT";
        case -0x7ff8d4f0:
switchD_005c0f97_caseD_80072b10:
          return (int)"WSA_QOS_EUNKOWNPSOBJ";
        case -0x7ff8d4ef:
switchD_005c0f97_caseD_80072b11:
          return (int)"WSA_QOS_EPOLICYOBJ";
        case -0x7ff8d4ee:
switchD_005c0f97_caseD_80072b12:
          return (int)"WSA_QOS_EFLOWDESC";
        case -0x7ff8d4ed:
switchD_005c0f97_caseD_80072b13:
          return (int)"WSA_QOS_EPSFLOWSPEC";
        case -0x7ff8d4ec:
switchD_005c0f97_caseD_80072b14:
          return (int)"WSA_QOS_EPSFILTERSPEC";
        case -0x7ff8d4eb:
switchD_005c0f97_caseD_80072b15:
          return (int)"WSA_QOS_ESDMODEOBJ";
        case -0x7ff8d4ea:
switchD_005c0f97_caseD_80072b16:
          return (int)"WSA_QOS_ESHAPERATEOBJ";
        case -0x7ff8d4e9:
switchD_005c0f97_caseD_80072b17:
          return (int)"WSA_QOS_RESERVED_PETYPE";
        }
      }
      else if (in_stack_00000004 < -0x7ff8ca17) {
        if (in_stack_00000004 == -0x7ff8ca18) {
LAB_005c8e16:
          return (int)"ERROR_IPSEC_IKE_NEG_STATUS_BEGIN";
        }
        switch(in_stack_00000004) {
        case -0x7ff8cd37:
switchD_005c0fbb_caseD_800732c9:
          return (int)"ERROR_IPSEC_QM_POLICY_NOT_FOUND";
        case -0x7ff8cd36:
switchD_005c0fbb_caseD_800732ca:
          return (int)"ERROR_IPSEC_QM_POLICY_IN_USE";
        case -0x7ff8cd35:
switchD_005c0fbb_caseD_800732cb:
          return (int)"ERROR_IPSEC_MM_POLICY_EXISTS";
        case -0x7ff8cd34:
switchD_005c0fbb_caseD_800732cc:
          return (int)"ERROR_IPSEC_MM_POLICY_NOT_FOUND";
        case -0x7ff8cd33:
switchD_005c0fbb_caseD_800732cd:
          return (int)"ERROR_IPSEC_MM_POLICY_IN_USE";
        case -0x7ff8cd32:
switchD_005c0fbb_caseD_800732ce:
          return (int)"ERROR_IPSEC_MM_FILTER_EXISTS";
        case -0x7ff8cd31:
switchD_005c0fbb_caseD_800732cf:
          return (int)"ERROR_IPSEC_MM_FILTER_NOT_FOUND";
        case -0x7ff8cd30:
          goto switchD_005c0fbb_caseD_800732d0;
        case -0x7ff8cd2f:
switchD_005c0fbb_caseD_800732d1:
          return (int)"ERROR_IPSEC_TRANSPORT_FILTER_NOT_FOUND";
        case -0x7ff8cd2e:
switchD_005c0fbb_caseD_800732d2:
          return (int)"ERROR_IPSEC_MM_AUTH_EXISTS";
        case -0x7ff8cd2d:
switchD_005c0fbb_caseD_800732d3:
          return (int)"ERROR_IPSEC_MM_AUTH_NOT_FOUND";
        case -0x7ff8cd2c:
switchD_005c0fbb_caseD_800732d4:
          return (int)"ERROR_IPSEC_MM_AUTH_IN_USE";
        case -0x7ff8cd2b:
switchD_005c0fbb_caseD_800732d5:
          return (int)"ERROR_IPSEC_DEFAULT_MM_POLICY_NOT_FOUND";
        case -0x7ff8cd2a:
switchD_005c0fbb_caseD_800732d6:
          return (int)"ERROR_IPSEC_DEFAULT_MM_AUTH_NOT_FOUND";
        case -0x7ff8cd29:
switchD_005c0fbb_caseD_800732d7:
          return (int)"ERROR_IPSEC_DEFAULT_QM_POLICY_NOT_FOUND";
        case -0x7ff8cd28:
switchD_005c0fbb_caseD_800732d8:
          return (int)"ERROR_IPSEC_TUNNEL_FILTER_EXISTS";
        case -0x7ff8cd27:
switchD_005c0fbb_caseD_800732d9:
          return (int)"ERROR_IPSEC_TUNNEL_FILTER_NOT_FOUND";
        case -0x7ff8cd26:
switchD_005c0fbb_caseD_800732da:
          return (int)"ERROR_IPSEC_MM_FILTER_PENDING_DELETION";
        case -0x7ff8cd25:
switchD_005c0fbb_caseD_800732db:
          return (int)"ERROR_IPSEC_TRANSPORT_FILTER_PENDING_DELETION";
        case -0x7ff8cd24:
switchD_005c0fbb_caseD_800732dc:
          return (int)"ERROR_IPSEC_TUNNEL_FILTER_PENDING_DELETION";
        case -0x7ff8cd23:
switchD_005c0fbb_caseD_800732dd:
          return (int)"ERROR_IPSEC_MM_POLICY_PENDING_DELETION";
        case -0x7ff8cd22:
switchD_005c0fbb_caseD_800732de:
          return (int)"ERROR_IPSEC_MM_AUTH_PENDING_DELETION";
        case -0x7ff8cd21:
switchD_005c0fbb_caseD_800732df:
          return (int)"ERROR_IPSEC_QM_POLICY_PENDING_DELETION";
        case -0x7ff8cd20:
switchD_005c0fbb_caseD_800732e0:
          return (int)"WARNING_IPSEC_MM_POLICY_PRUNED";
        case -0x7ff8cd1f:
switchD_005c0fbb_caseD_800732e1:
          return (int)"WARNING_IPSEC_QM_POLICY_PRUNED";
        }
      }
      else {
        switch(in_stack_00000004) {
        case -0x7ff8ca17:
switchD_005c0fd9_caseD_800735e9:
          return (int)"ERROR_IPSEC_IKE_AUTH_FAIL";
        case -0x7ff8ca16:
switchD_005c0fd9_caseD_800735ea:
          return (int)"ERROR_IPSEC_IKE_ATTRIB_FAIL";
        case -0x7ff8ca15:
switchD_005c0fd9_caseD_800735eb:
          return (int)"ERROR_IPSEC_IKE_NEGOTIATION_PENDING";
        case -0x7ff8ca14:
switchD_005c0fd9_caseD_800735ec:
          return (int)"ERROR_IPSEC_IKE_GENERAL_PROCESSING_ERROR";
        case -0x7ff8ca13:
switchD_005c0fd9_caseD_800735ed:
          return (int)"ERROR_IPSEC_IKE_TIMED_OUT";
        case -0x7ff8ca12:
switchD_005c0fd9_caseD_800735ee:
          return (int)"ERROR_IPSEC_IKE_NO_CERT";
        case -0x7ff8ca11:
switchD_005c0fd9_caseD_800735ef:
          return (int)"ERROR_IPSEC_IKE_SA_DELETED";
        case -0x7ff8ca10:
switchD_005c0fd9_caseD_800735f0:
          return (int)"ERROR_IPSEC_IKE_SA_REAPED";
        case -0x7ff8ca0f:
switchD_005c0fd9_caseD_800735f1:
          return (int)"ERROR_IPSEC_IKE_MM_ACQUIRE_DROP";
        case -0x7ff8ca0e:
switchD_005c0fd9_caseD_800735f2:
          return (int)"ERROR_IPSEC_IKE_QM_ACQUIRE_DROP";
        case -0x7ff8ca0d:
switchD_005c0fd9_caseD_800735f3:
          return (int)"ERROR_IPSEC_IKE_QUEUE_DROP_MM";
        case -0x7ff8ca0c:
switchD_005c0fd9_caseD_800735f4:
          return (int)"ERROR_IPSEC_IKE_QUEUE_DROP_NO_MM";
        case -0x7ff8ca0b:
switchD_005c0fd9_caseD_800735f5:
          return (int)"ERROR_IPSEC_IKE_DROP_NO_RESPONSE";
        case -0x7ff8ca0a:
switchD_005c0fd9_caseD_800735f6:
          return (int)"ERROR_IPSEC_IKE_MM_DELAY_DROP";
        case -0x7ff8ca09:
switchD_005c0fd9_caseD_800735f7:
          return (int)"ERROR_IPSEC_IKE_QM_DELAY_DROP";
        case -0x7ff8ca08:
switchD_005c0fd9_caseD_800735f8:
          return (int)"ERROR_IPSEC_IKE_ERROR";
        case -0x7ff8ca07:
switchD_005c0fd9_caseD_800735f9:
          return (int)"ERROR_IPSEC_IKE_CRL_FAILED";
        case -0x7ff8ca06:
switchD_005c0fd9_caseD_800735fa:
          return (int)"ERROR_IPSEC_IKE_INVALID_KEY_USAGE";
        case -0x7ff8ca05:
switchD_005c0fd9_caseD_800735fb:
          return (int)"ERROR_IPSEC_IKE_INVALID_CERT_TYPE";
        case -0x7ff8ca04:
switchD_005c0fd9_caseD_800735fc:
          return (int)"ERROR_IPSEC_IKE_NO_PRIVATE_KEY";
        case -0x7ff8ca02:
switchD_005c0fd9_caseD_800735fe:
          return (int)"ERROR_IPSEC_IKE_DH_FAIL";
        case -0x7ff8ca00:
switchD_005c0fd9_caseD_80073600:
          return (int)"ERROR_IPSEC_IKE_INVALID_HEADER";
        case -0x7ff8c9ff:
switchD_005c0fd9_caseD_80073601:
          return (int)"ERROR_IPSEC_IKE_NO_POLICY";
        case -0x7ff8c9fe:
switchD_005c0fd9_caseD_80073602:
          return (int)"ERROR_IPSEC_IKE_INVALID_SIGNATURE";
        case -0x7ff8c9fd:
switchD_005c0fd9_caseD_80073603:
          return (int)"ERROR_IPSEC_IKE_KERBEROS_ERROR";
        case -0x7ff8c9fc:
switchD_005c0fd9_caseD_80073604:
          return (int)"ERROR_IPSEC_IKE_NO_PUBLIC_KEY";
        case -0x7ff8c9fb:
switchD_005c0fd9_caseD_80073605:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR";
        case -0x7ff8c9fa:
switchD_005c0fd9_caseD_80073606:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_SA";
        case -0x7ff8c9f9:
switchD_005c0fd9_caseD_80073607:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_PROP";
        case -0x7ff8c9f8:
switchD_005c0fd9_caseD_80073608:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_TRANS";
        case -0x7ff8c9f7:
switchD_005c0fd9_caseD_80073609:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_KE";
        case -0x7ff8c9f6:
switchD_005c0fd9_caseD_8007360a:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_ID";
        case -0x7ff8c9f5:
switchD_005c0fd9_caseD_8007360b:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_CERT";
        case -0x7ff8c9f4:
switchD_005c0fd9_caseD_8007360c:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_CERT_REQ";
        case -0x7ff8c9f3:
switchD_005c0fd9_caseD_8007360d:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_HASH";
        case -0x7ff8c9f2:
switchD_005c0fd9_caseD_8007360e:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_SIG";
        case -0x7ff8c9f1:
switchD_005c0fd9_caseD_8007360f:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_NONCE";
        case -0x7ff8c9f0:
switchD_005c0fd9_caseD_80073610:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_NOTIFY";
        case -0x7ff8c9ef:
switchD_005c0fd9_caseD_80073611:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_DELETE";
        case -0x7ff8c9ee:
switchD_005c0fd9_caseD_80073612:
          return (int)"ERROR_IPSEC_IKE_PROCESS_ERR_VENDOR";
        case -0x7ff8c9ed:
switchD_005c0fd9_caseD_80073613:
          return (int)"ERROR_IPSEC_IKE_INVALID_PAYLOAD";
        case -0x7ff8c9ec:
          goto switchD_005c0fd9_caseD_80073614;
        case -0x7ff8c9eb:
          goto switchD_005c0fd9_caseD_80073615;
        case -0x7ff8c9ea:
          goto switchD_005c0fd9_caseD_80073616;
        case -0x7ff8c9e9:
          goto switchD_005c0fd9_caseD_80073617;
        case -0x7ff8c9e8:
          goto switchD_005c0fd9_caseD_80073618;
        case -0x7ff8c9e7:
          goto switchD_005c0fd9_caseD_80073619;
        case -0x7ff8c9e6:
          goto switchD_005c0fd9_caseD_8007361a;
        case -0x7ff8c9e5:
          goto switchD_005c0fd9_caseD_8007361b;
        case -0x7ff8c9e4:
          goto switchD_005c0fd9_caseD_8007361c;
        case -0x7ff8c9e3:
          goto switchD_005c0fd9_caseD_8007361d;
        case -0x7ff8c9e2:
          goto switchD_005c0fd9_caseD_8007361e;
        case -0x7ff8c9e1:
          goto switchD_005c0fd9_caseD_8007361f;
        case -0x7ff8c9e0:
          goto switchD_005c0fd9_caseD_80073620;
        case -0x7ff8c9df:
          goto switchD_005c0fd9_caseD_80073621;
        case -0x7ff8c9de:
          goto switchD_005c0fd9_caseD_80073622;
        case -0x7ff8c9dd:
          goto switchD_005c0fd9_caseD_80073623;
        case -0x7ff8c9dc:
          goto switchD_005c0fd9_caseD_80073624;
        case -0x7ff8c9db:
          goto switchD_005c0fd9_caseD_80073625;
        case -0x7ff8c9da:
          goto switchD_005c0fd9_caseD_80073626;
        case -0x7ff8c9d9:
          goto switchD_005c0fd9_caseD_80073627;
        case -0x7ff8c9d8:
          goto switchD_005c0fd9_caseD_80073628;
        case -0x7ff8c9d7:
          goto switchD_005c0fd9_caseD_80073629;
        case -0x7ff8c9d6:
          goto switchD_005c0fd9_caseD_8007362a;
        case -0x7ff8c9d5:
          goto switchD_005c0fd9_caseD_8007362b;
        case -0x7ff8c9d4:
          goto switchD_005c0fd9_caseD_8007362c;
        case -0x7ff8c9d3:
          goto switchD_005c0fd9_caseD_8007362d;
        case -0x7ff8c9d2:
          goto switchD_005c0fd9_caseD_8007362e;
        case -0x7ff8c9d1:
          goto switchD_005c0fd9_caseD_8007362f;
        case -0x7ff8c9d0:
          goto switchD_005c0fd9_caseD_80073630;
        case -0x7ff8c9cf:
          goto switchD_005c0fd9_caseD_80073631;
        case -0x7ff8c9ce:
          goto switchD_005c0fd9_caseD_80073632;
        case -0x7ff8c9cd:
          goto switchD_005c0fd9_caseD_80073633;
        case -0x7ff8c9cc:
          goto switchD_005c0fd9_caseD_80073634;
        case -0x7ff8c9cb:
          goto switchD_005c0fd9_caseD_80073635;
        case -0x7ff8c9ca:
          goto switchD_005c0fd9_caseD_80073636;
        case -0x7ff8c9c9:
          goto switchD_005c0fd9_caseD_80073637;
        case -0x7ff8c9c7:
          goto switchD_005c0fd9_caseD_80073639;
        case -0x7ff8c9c6:
          goto switchD_005c0fd9_caseD_8007363a;
        case -0x7ff8c9c5:
          goto switchD_005c0fd9_caseD_8007363b;
        case -0x7ff8c9c4:
          goto switchD_005c0fd9_caseD_8007363c;
        case -0x7ff8c950:
          goto switchD_005c0fd9_caseD_800736b0;
        case -0x7ff8c94f:
          goto switchD_005c0fd9_caseD_800736b1;
        case -0x7ff8c94e:
          goto switchD_005c0fd9_caseD_800736b2;
        case -0x7ff8c94d:
          goto switchD_005c0fd9_caseD_800736b3;
        case -0x7ff8c94c:
          goto switchD_005c0fd9_caseD_800736b4;
        case -0x7ff8c94b:
          goto switchD_005c0fd9_caseD_800736b5;
        case -0x7ff8c94a:
          goto switchD_005c0fd9_caseD_800736b6;
        case -0x7ff8c949:
          goto switchD_005c0fd9_caseD_800736b7;
        case -0x7ff8c948:
          goto switchD_005c0fd9_caseD_800736b8;
        case -0x7ff8c947:
          goto switchD_005c0fd9_caseD_800736b9;
        case -0x7ff8c946:
          goto switchD_005c0fd9_caseD_800736ba;
        case -0x7ff8c945:
          goto switchD_005c0fd9_caseD_800736bb;
        case -0x7ff8c944:
          goto switchD_005c0fd9_caseD_800736bc;
        case -0x7ff8c943:
          goto switchD_005c0fd9_caseD_800736bd;
        case -0x7ff8c942:
          goto switchD_005c0fd9_caseD_800736be;
        case -0x7ff8c941:
          goto switchD_005c0fd9_caseD_800736bf;
        case -0x7ff8c940:
          goto switchD_005c0fd9_caseD_800736c0;
        case -0x7ff8c93f:
          goto switchD_005c0fd9_caseD_800736c1;
        case -0x7ff8c93e:
          goto switchD_005c0fd9_caseD_800736c2;
        case -0x7ff8c93d:
          goto switchD_005c0fd9_caseD_800736c3;
        case -0x7ff8c93c:
          goto switchD_005c0fd9_caseD_800736c4;
        case -0x7ff8c93b:
          goto switchD_005c0fd9_caseD_800736c5;
        case -0x7ff8c93a:
          goto switchD_005c0fd9_caseD_800736c6;
        }
      }
    }
    else if (in_stack_00000004 < -0x7ff7fffe) {
      if (in_stack_00000004 == -0x7ff7ffff) {
        return (int)"CO_E_CLASS_CREATE_FAILED";
      }
      switch(in_stack_00000004) {
      case -0x7ff8c938:
switchD_005c0ff9_caseD_800736c8:
        return (int)"ERROR_SXS_DUPLICATE_IID";
      case -0x7ff8c937:
switchD_005c0ff9_caseD_800736c9:
        return (int)"ERROR_SXS_DUPLICATE_TLBID";
      case -0x7ff8c936:
switchD_005c0ff9_caseD_800736ca:
        return (int)"ERROR_SXS_DUPLICATE_PROGID";
      case -0x7ff8c935:
switchD_005c0ff9_caseD_800736cb:
        return (int)"ERROR_SXS_DUPLICATE_ASSEMBLY_NAME";
      case -0x7ff8c934:
switchD_005c0ff9_caseD_800736cc:
        return (int)"ERROR_SXS_FILE_HASH_MISMATCH";
      case -0x7ff8c933:
switchD_005c0ff9_caseD_800736cd:
        return (int)"ERROR_SXS_POLICY_PARSE_ERROR";
      case -0x7ff8c932:
switchD_005c0ff9_caseD_800736ce:
        return (int)"ERROR_SXS_XML_E_MISSINGQUOTE";
      case -0x7ff8c931:
switchD_005c0ff9_caseD_800736cf:
        return (int)"ERROR_SXS_XML_E_COMMENTSYNTAX";
      case -0x7ff8c930:
switchD_005c0ff9_caseD_800736d0:
        return (int)"ERROR_SXS_XML_E_BADSTARTNAMECHAR";
      case -0x7ff8c92f:
switchD_005c0ff9_caseD_800736d1:
        return (int)"ERROR_SXS_XML_E_BADNAMECHAR";
      case -0x7ff8c92e:
switchD_005c0ff9_caseD_800736d2:
        return (int)"ERROR_SXS_XML_E_BADCHARINSTRING";
      case -0x7ff8c92d:
switchD_005c0ff9_caseD_800736d3:
        return (int)"ERROR_SXS_XML_E_XMLDECLSYNTAX";
      case -0x7ff8c92c:
switchD_005c0ff9_caseD_800736d4:
        return (int)"ERROR_SXS_XML_E_BADCHARDATA";
      case -0x7ff8c92b:
switchD_005c0ff9_caseD_800736d5:
        return (int)"ERROR_SXS_XML_E_MISSINGWHITESPACE";
      case -0x7ff8c92a:
switchD_005c0ff9_caseD_800736d6:
        return (int)"ERROR_SXS_XML_E_EXPECTINGTAGEND";
      case -0x7ff8c929:
switchD_005c0ff9_caseD_800736d7:
        return (int)"ERROR_SXS_XML_E_MISSINGSEMICOLON";
      case -0x7ff8c928:
switchD_005c0ff9_caseD_800736d8:
        return (int)"ERROR_SXS_XML_E_UNBALANCEDPAREN";
      case -0x7ff8c927:
switchD_005c0ff9_caseD_800736d9:
        return (int)"ERROR_SXS_XML_E_INTERNALERROR";
      case -0x7ff8c926:
switchD_005c0ff9_caseD_800736da:
        return (int)"ERROR_SXS_XML_E_UNEXPECTED_WHITESPACE";
      case -0x7ff8c925:
switchD_005c0ff9_caseD_800736db:
        return (int)"ERROR_SXS_XML_E_INCOMPLETE_ENCODING";
      case -0x7ff8c924:
switchD_005c0ff9_caseD_800736dc:
        return (int)"ERROR_SXS_XML_E_MISSING_PAREN";
      case -0x7ff8c923:
switchD_005c0ff9_caseD_800736dd:
        return (int)"ERROR_SXS_XML_E_EXPECTINGCLOSEQUOTE";
      case -0x7ff8c922:
switchD_005c0ff9_caseD_800736de:
        return (int)"ERROR_SXS_XML_E_MULTIPLE_COLONS";
      case -0x7ff8c921:
switchD_005c0ff9_caseD_800736df:
        return (int)"ERROR_SXS_XML_E_INVALID_DECIMAL";
      case -0x7ff8c920:
switchD_005c0ff9_caseD_800736e0:
        return (int)"ERROR_SXS_XML_E_INVALID_HEXIDECIMAL";
      case -0x7ff8c91f:
switchD_005c0ff9_caseD_800736e1:
        return (int)"ERROR_SXS_XML_E_INVALID_UNICODE";
      case -0x7ff8c91e:
switchD_005c0ff9_caseD_800736e2:
        return (int)"ERROR_SXS_XML_E_WHITESPACEORQUESTIONMARK";
      case -0x7ff8c91d:
switchD_005c0ff9_caseD_800736e3:
        return (int)"ERROR_SXS_XML_E_UNEXPECTEDENDTAG";
      case -0x7ff8c91c:
switchD_005c0ff9_caseD_800736e4:
        return (int)"ERROR_SXS_XML_E_UNCLOSEDTAG";
      case -0x7ff8c91b:
switchD_005c0ff9_caseD_800736e5:
        return (int)"ERROR_SXS_XML_E_DUPLICATEATTRIBUTE";
      case -0x7ff8c91a:
switchD_005c0ff9_caseD_800736e6:
        return (int)"ERROR_SXS_XML_E_MULTIPLEROOTS";
      case -0x7ff8c919:
switchD_005c0ff9_caseD_800736e7:
        return (int)"ERROR_SXS_XML_E_INVALIDATROOTLEVEL";
      case -0x7ff8c918:
switchD_005c0ff9_caseD_800736e8:
        return (int)"ERROR_SXS_XML_E_BADXMLDECL";
      case -0x7ff8c917:
switchD_005c0ff9_caseD_800736e9:
        return (int)"ERROR_SXS_XML_E_MISSINGROOT";
      case -0x7ff8c916:
switchD_005c0ff9_caseD_800736ea:
        return (int)"ERROR_SXS_XML_E_UNEXPECTEDEOF";
      case -0x7ff8c915:
switchD_005c0ff9_caseD_800736eb:
        return (int)"ERROR_SXS_XML_E_BADPEREFINSUBSET";
      case -0x7ff8c914:
switchD_005c0ff9_caseD_800736ec:
        return (int)"ERROR_SXS_XML_E_UNCLOSEDSTARTTAG";
      case -0x7ff8c913:
switchD_005c0ff9_caseD_800736ed:
        return (int)"ERROR_SXS_XML_E_UNCLOSEDENDTAG";
      case -0x7ff8c912:
switchD_005c0ff9_caseD_800736ee:
        return (int)"ERROR_SXS_XML_E_UNCLOSEDSTRING";
      case -0x7ff8c911:
switchD_005c0ff9_caseD_800736ef:
        return (int)"ERROR_SXS_XML_E_UNCLOSEDCOMMENT";
      case -0x7ff8c910:
switchD_005c0ff9_caseD_800736f0:
        return (int)"ERROR_SXS_XML_E_UNCLOSEDDECL";
      case -0x7ff8c90f:
switchD_005c0ff9_caseD_800736f1:
        return (int)"ERROR_SXS_XML_E_UNCLOSEDCDATA";
      case -0x7ff8c90e:
switchD_005c0ff9_caseD_800736f2:
        return (int)"ERROR_SXS_XML_E_RESERVEDNAMESPACE";
      case -0x7ff8c90d:
switchD_005c0ff9_caseD_800736f3:
        return (int)"ERROR_SXS_XML_E_INVALIDENCODING";
      case -0x7ff8c90c:
switchD_005c0ff9_caseD_800736f4:
        return (int)"ERROR_SXS_XML_E_INVALIDSWITCH";
      case -0x7ff8c90b:
switchD_005c0ff9_caseD_800736f5:
        return (int)"ERROR_SXS_XML_E_BADXMLCASE";
      case -0x7ff8c90a:
switchD_005c0ff9_caseD_800736f6:
        return (int)"ERROR_SXS_XML_E_INVALID_STANDALONE";
      case -0x7ff8c909:
switchD_005c0ff9_caseD_800736f7:
        return (int)"ERROR_SXS_XML_E_UNEXPECTED_STANDALONE";
      case -0x7ff8c908:
switchD_005c0ff9_caseD_800736f8:
        return (int)"ERROR_SXS_XML_E_INVALID_VERSION";
      case -0x7ff8c907:
switchD_005c0ff9_caseD_800736f9:
        return (int)"ERROR_SXS_XML_E_MISSINGEQUALS";
      case -0x7ff8c906:
switchD_005c0ff9_caseD_800736fa:
        return (int)"ERROR_SXS_PROTECTION_RECOVERY_FAILED";
      case -0x7ff8c905:
switchD_005c0ff9_caseD_800736fb:
        return (int)"ERROR_SXS_PROTECTION_PUBLIC_KEY_TOO_SHORT";
      case -0x7ff8c904:
switchD_005c0ff9_caseD_800736fc:
        return (int)"ERROR_SXS_PROTECTION_CATALOG_NOT_VALID";
      case -0x7ff8c903:
switchD_005c0ff9_caseD_800736fd:
        return (int)"ERROR_SXS_UNTRANSLATABLE_HRESULT";
      case -0x7ff8c902:
switchD_005c0ff9_caseD_800736fe:
        return (int)"ERROR_SXS_PROTECTION_CATALOG_FILE_MISSING";
      case -0x7ff8c901:
switchD_005c0ff9_caseD_800736ff:
        return (int)"ERROR_SXS_MISSING_ASSEMBLY_IDENTITY_ATTRIBUTE";
      case -0x7ff8c900:
switchD_005c0ff9_caseD_80073700:
        return (int)"ERROR_SXS_INVALID_ASSEMBLY_IDENTITY_ATTRIBUTE_NAME";
      }
    }
    else if (in_stack_00000004 < -0x7ff6fffe) {
      if (in_stack_00000004 == -0x7ff6ffff) {
        return (int)"NTE_BAD_UID";
      }
      switch(in_stack_00000004) {
      case -0x7ff7fffe:
        return (int)"CO_E_SCM_ERROR";
      case -0x7ff7fffd:
        return (int)"CO_E_SCM_RPC_FAILURE";
      case -0x7ff7fffc:
        return (int)"CO_E_BAD_PATH";
      case -0x7ff7fffb:
        return (int)"CO_E_SERVER_EXEC_FAILURE";
      case -0x7ff7fffa:
        return (int)"CO_E_OBJSRV_RPC_FAILURE";
      case -0x7ff7fff9:
        return (int)"MK_E_NO_NORMALIZED";
      case -0x7ff7fff8:
        return (int)"CO_E_SERVER_STOPPING";
      case -0x7ff7fff7:
        return (int)"MEM_E_INVALID_ROOT";
      case -0x7ff7fff0:
        return (int)"MEM_E_INVALID_LINK";
      case -0x7ff7ffef:
        return (int)"MEM_E_INVALID_SIZE";
      }
    }
    else if (in_stack_00000004 < -0x7ff6fcff) {
      if (in_stack_00000004 == -0x7ff6fd00) {
        return (int)"SEC_E_INSUFFICIENT_MEMORY";
      }
      switch(in_stack_00000004) {
      case -0x7ff6fffe:
        return (int)"NTE_BAD_HASH";
      case -0x7ff6fffd:
        return (int)"NTE_BAD_KEY";
      case -0x7ff6fffc:
        return (int)"NTE_BAD_LEN";
      case -0x7ff6fffb:
        return (int)"NTE_BAD_DATA";
      case -0x7ff6fffa:
        return (int)"NTE_BAD_SIGNATURE";
      case -0x7ff6fff9:
        return (int)"NTE_BAD_VER";
      case -0x7ff6fff8:
        return (int)"NTE_BAD_ALGID";
      case -0x7ff6fff7:
        return (int)"NTE_BAD_FLAGS";
      case -0x7ff6fff6:
        return (int)"NTE_BAD_TYPE";
      case -0x7ff6fff5:
        return (int)"NTE_BAD_KEY_STATE";
      case -0x7ff6fff4:
        return (int)"NTE_BAD_HASH_STATE";
      case -0x7ff6fff3:
        return (int)"NTE_NO_KEY";
      case -0x7ff6fff2:
        return (int)"NTE_NO_MEMORY";
      case -0x7ff6fff1:
        return (int)"NTE_EXISTS";
      case -0x7ff6fff0:
        return (int)"NTE_PERM";
      case -0x7ff6ffef:
        return (int)"NTE_NOT_FOUND";
      case -0x7ff6ffee:
        return (int)"NTE_DOUBLE_ENCRYPT";
      case -0x7ff6ffed:
        return (int)"NTE_BAD_PROVIDER";
      case -0x7ff6ffec:
        return (int)"NTE_BAD_PROV_TYPE";
      case -0x7ff6ffeb:
        return (int)"NTE_BAD_PUBLIC_KEY";
      case -0x7ff6ffea:
        return (int)"NTE_BAD_KEYSET";
      case -0x7ff6ffe9:
        return (int)"NTE_PROV_TYPE_NOT_DEF";
      case -0x7ff6ffe8:
        return (int)"NTE_PROV_TYPE_ENTRY_BAD";
      case -0x7ff6ffe7:
        return (int)"NTE_KEYSET_NOT_DEF";
      case -0x7ff6ffe6:
        return (int)"NTE_KEYSET_ENTRY_BAD";
      case -0x7ff6ffe5:
        return (int)"NTE_PROV_TYPE_NO_MATCH";
      case -0x7ff6ffe4:
        return (int)"NTE_SIGNATURE_FILE_BAD";
      case -0x7ff6ffe3:
        return (int)"NTE_PROVIDER_DLL_FAIL";
      case -0x7ff6ffe2:
        return (int)"NTE_PROV_DLL_NOT_FOUND";
      case -0x7ff6ffe1:
        return (int)"NTE_BAD_KEYSET_PARAM";
      case -0x7ff6ffe0:
        return (int)"NTE_FAIL";
      case -0x7ff6ffdf:
        return (int)"NTE_SYS_ERR";
      case -0x7ff6ffde:
        return (int)"NTE_SILENT_CONTEXT";
      case -0x7ff6ffdd:
        return (int)"NTE_TOKEN_KEYSET_STORAGE_FULL";
      case -0x7ff6ffdc:
        return (int)"NTE_TEMPORARY_PROFILE";
      case -0x7ff6ffdb:
        return (int)"NTE_FIXEDPARAMETER";
      }
    }
    else if (in_stack_00000004 < -0x7ff6effe) {
      if (in_stack_00000004 == -0x7ff6efff) {
        return (int)"CRYPT_E_MSG_ERROR";
      }
      switch(in_stack_00000004) {
      case -0x7ff6fcff:
        return (int)"SEC_E_INVALID_HANDLE";
      case -0x7ff6fcfe:
        return (int)"SEC_E_UNSUPPORTED_FUNCTION";
      case -0x7ff6fcfd:
        return (int)"SEC_E_TARGET_UNKNOWN";
      case -0x7ff6fcfc:
        return (int)"SEC_E_INTERNAL_ERROR";
      case -0x7ff6fcfb:
        return (int)"SEC_E_SECPKG_NOT_FOUND";
      case -0x7ff6fcfa:
        return (int)"SEC_E_NOT_OWNER";
      case -0x7ff6fcf9:
        return (int)"SEC_E_CANNOT_INSTALL";
      case -0x7ff6fcf8:
        return (int)"SEC_E_INVALID_TOKEN";
      case -0x7ff6fcf7:
        return (int)"SEC_E_CANNOT_PACK";
      case -0x7ff6fcf6:
        return (int)"SEC_E_QOP_NOT_SUPPORTED";
      case -0x7ff6fcf5:
        return (int)"SEC_E_NO_IMPERSONATION";
      case -0x7ff6fcf4:
        return (int)"SEC_E_LOGON_DENIED";
      case -0x7ff6fcf3:
        return (int)"SEC_E_UNKNOWN_CREDENTIALS";
      case -0x7ff6fcf2:
        return (int)"SEC_E_NO_CREDENTIALS";
      case -0x7ff6fcf1:
        return (int)"SEC_E_MESSAGE_ALTERED";
      case -0x7ff6fcf0:
        return (int)"SEC_E_OUT_OF_SEQUENCE";
      case -0x7ff6fcef:
        return (int)"SEC_E_NO_AUTHENTICATING_AUTHORITY";
      case -0x7ff6fcea:
        return (int)"SEC_E_BAD_PKGID";
      case -0x7ff6fce9:
        return (int)"SEC_E_CONTEXT_EXPIRED";
      case -0x7ff6fce8:
        return (int)"SEC_E_INCOMPLETE_MESSAGE";
      case -0x7ff6fce0:
        return (int)"SEC_E_INCOMPLETE_CREDENTIALS";
      case -0x7ff6fcdf:
        return (int)"SEC_E_BUFFER_TOO_SMALL";
      case -0x7ff6fcde:
        return (int)"SEC_E_WRONG_PRINCIPAL";
      case -0x7ff6fcdc:
        return (int)"SEC_E_TIME_SKEW";
      case -0x7ff6fcdb:
        return (int)"SEC_E_UNTRUSTED_ROOT";
      case -0x7ff6fcda:
        return (int)"SEC_E_ILLEGAL_MESSAGE";
      case -0x7ff6fcd9:
        return (int)"SEC_E_CERT_UNKNOWN";
      case -0x7ff6fcd8:
        return (int)"SEC_E_CERT_EXPIRED";
      case -0x7ff6fcd7:
        return (int)"SEC_E_ENCRYPT_FAILURE";
      case -0x7ff6fcd0:
        return (int)"SEC_E_DECRYPT_FAILURE";
      case -0x7ff6fccf:
        return (int)"SEC_E_ALGORITHM_MISMATCH";
      case -0x7ff6fcce:
        return (int)"SEC_E_SECURITY_QOS_FAILED";
      case -0x7ff6fccd:
        return (int)"SEC_E_UNFINISHED_CONTEXT_DELETED";
      case -0x7ff6fccc:
        return (int)"SEC_E_NO_TGT_REPLY";
      case -0x7ff6fccb:
        return (int)"SEC_E_NO_IP_ADDRESSES";
      case -0x7ff6fcca:
        return (int)"SEC_E_WRONG_CREDENTIAL_HANDLE";
      case -0x7ff6fcc9:
        return (int)"SEC_E_CRYPTO_SYSTEM_INVALID";
      case -0x7ff6fcc8:
        return (int)"SEC_E_MAX_REFERRALS_EXCEEDED";
      case -0x7ff6fcc7:
        return (int)"SEC_E_MUST_BE_KDC";
      case -0x7ff6fcc6:
        return (int)"SEC_E_STRONG_CRYPTO_NOT_SUPPORTED";
      case -0x7ff6fcc5:
        return (int)"SEC_E_TOO_MANY_PRINCIPALS";
      case -0x7ff6fcc4:
        return (int)"SEC_E_NO_PA_DATA";
      case -0x7ff6fcc3:
        return (int)"SEC_E_PKINIT_NAME_MISMATCH";
      case -0x7ff6fcc2:
        return (int)"SEC_E_SMARTCARD_LOGON_REQUIRED";
      case -0x7ff6fcc1:
        return (int)"SEC_E_SHUTDOWN_IN_PROGRESS";
      case -0x7ff6fcc0:
        return (int)"SEC_E_KDC_INVALID_REQUEST";
      case -0x7ff6fcbf:
        return (int)"SEC_E_KDC_UNABLE_TO_REFER";
      case -0x7ff6fcbe:
        return (int)"SEC_E_KDC_UNKNOWN_ETYPE";
      case -0x7ff6fcbd:
        return (int)"SEC_E_UNSUPPORTED_PREAUTH";
      case -0x7ff6fcbb:
        return (int)"SEC_E_DELEGATION_REQUIRED";
      case -0x7ff6fcba:
        return (int)"SEC_E_BAD_BINDINGS";
      case -0x7ff6fcb9:
        return (int)"SEC_E_MULTIPLE_ACCOUNTS";
      case -0x7ff6fcb8:
        return (int)"SEC_E_NO_KERB_KEY";
      case -0x7ff6fcb7:
        return (int)"SEC_E_CERT_WRONG_USAGE";
      }
    }
    else if (in_stack_00000004 < -0x7ff6dffe) {
      if (in_stack_00000004 == -0x7ff6dfff) {
        return (int)"CRYPT_E_BAD_LEN";
      }
      switch(in_stack_00000004) {
      case -0x7ff6effe:
        return (int)"CRYPT_E_UNKNOWN_ALGO";
      case -0x7ff6effd:
        return (int)"CRYPT_E_OID_FORMAT";
      case -0x7ff6effc:
        return (int)"CRYPT_E_INVALID_MSG_TYPE";
      case -0x7ff6effb:
        return (int)"CRYPT_E_UNEXPECTED_ENCODING";
      case -0x7ff6effa:
        return (int)"CRYPT_E_AUTH_ATTR_MISSING";
      case -0x7ff6eff9:
        return (int)"CRYPT_E_HASH_VALUE";
      case -0x7ff6eff8:
        return (int)"CRYPT_E_INVALID_INDEX";
      case -0x7ff6eff7:
        return (int)"CRYPT_E_ALREADY_DECRYPTED";
      case -0x7ff6eff6:
        return (int)"CRYPT_E_NOT_DECRYPTED";
      case -0x7ff6eff5:
        return (int)"CRYPT_E_RECIPIENT_NOT_FOUND";
      case -0x7ff6eff4:
        return (int)"CRYPT_E_CONTROL_TYPE";
      case -0x7ff6eff3:
        return (int)"CRYPT_E_ISSUER_SERIALNUMBER";
      case -0x7ff6eff2:
        return (int)"CRYPT_E_SIGNER_NOT_FOUND";
      case -0x7ff6eff1:
        return (int)"CRYPT_E_ATTRIBUTES_MISSING";
      case -0x7ff6eff0:
        return (int)"CRYPT_E_STREAM_MSG_NOT_READY";
      case -0x7ff6efef:
        return (int)"CRYPT_E_STREAM_INSUFFICIENT_DATA";
      }
    }
    else if (in_stack_00000004 < -0x7ff6cfff) {
      if (in_stack_00000004 == -0x7ff6d000) {
        return (int)"CRYPT_E_OSS_ERROR";
      }
      switch(in_stack_00000004) {
      case -0x7ff6dffe:
        return (int)"CRYPT_E_BAD_ENCODE";
      case -0x7ff6dffd:
        return (int)"CRYPT_E_FILE_ERROR";
      case -0x7ff6dffc:
        return (int)"CRYPT_E_NOT_FOUND";
      case -0x7ff6dffb:
        return (int)"CRYPT_E_EXISTS";
      case -0x7ff6dffa:
        return (int)"CRYPT_E_NO_PROVIDER";
      case -0x7ff6dff9:
        return (int)"CRYPT_E_SELF_SIGNED";
      case -0x7ff6dff8:
        return (int)"CRYPT_E_DELETED_PREV";
      case -0x7ff6dff7:
        return (int)"CRYPT_E_NO_MATCH";
      case -0x7ff6dff6:
        return (int)"CRYPT_E_UNEXPECTED_MSG_TYPE";
      case -0x7ff6dff5:
        return (int)"CRYPT_E_NO_KEY_PROPERTY";
      case -0x7ff6dff4:
        return (int)"CRYPT_E_NO_DECRYPT_CERT";
      case -0x7ff6dff3:
        return (int)"CRYPT_E_BAD_MSG";
      case -0x7ff6dff2:
        return (int)"CRYPT_E_NO_SIGNER";
      case -0x7ff6dff1:
        return (int)"CRYPT_E_PENDING_CLOSE";
      case -0x7ff6dff0:
        return (int)"CRYPT_E_REVOKED";
      case -0x7ff6dfef:
        return (int)"CRYPT_E_NO_REVOCATION_DLL";
      case -0x7ff6dfee:
        return (int)"CRYPT_E_NO_REVOCATION_CHECK";
      case -0x7ff6dfed:
        return (int)"CRYPT_E_REVOCATION_OFFLINE";
      case -0x7ff6dfec:
        return (int)"CRYPT_E_NOT_IN_REVOCATION_DATABASE";
      case -0x7ff6dfe0:
        return (int)"CRYPT_E_INVALID_NUMERIC_STRING";
      case -0x7ff6dfdf:
        return (int)"CRYPT_E_INVALID_PRINTABLE_STRING";
      case -0x7ff6dfde:
        return (int)"CRYPT_E_INVALID_IA5_STRING";
      case -0x7ff6dfdd:
        return (int)"CRYPT_E_INVALID_X500_STRING";
      case -0x7ff6dfdc:
        return (int)"CRYPT_E_NOT_CHAR_STRING";
      case -0x7ff6dfdb:
        return (int)"CRYPT_E_FILERESIZED";
      case -0x7ff6dfda:
        return (int)"CRYPT_E_SECURITY_SETTINGS";
      case -0x7ff6dfd9:
        return (int)"CRYPT_E_NO_VERIFY_USAGE_DLL";
      case -0x7ff6dfd8:
        return (int)"CRYPT_E_NO_VERIFY_USAGE_CHECK";
      case -0x7ff6dfd7:
        return (int)"CRYPT_E_VERIFY_USAGE_OFFLINE";
      case -0x7ff6dfd6:
        return (int)"CRYPT_E_NOT_IN_CTL";
      case -0x7ff6dfd5:
        return (int)"CRYPT_E_NO_TRUSTED_SIGNER";
      case -0x7ff6dfd4:
        return (int)"CRYPT_E_MISSING_PUBKEY_PARA";
      }
    }
    else if (in_stack_00000004 < -0x7ff6ceff) {
      if (in_stack_00000004 == -0x7ff6cf00) {
        return (int)"CRYPT_E_ASN1_ERROR";
      }
      switch(in_stack_00000004) {
      case -0x7ff6cfff:
        return (int)"OSS_MORE_BUF";
      case -0x7ff6cffe:
        return (int)"OSS_NEGATIVE_UINTEGER";
      case -0x7ff6cffd:
        return (int)"OSS_PDU_RANGE";
      case -0x7ff6cffc:
        return (int)"OSS_MORE_INPUT";
      case -0x7ff6cffb:
        return (int)"OSS_DATA_ERROR";
      case -0x7ff6cffa:
        return (int)"OSS_BAD_ARG";
      case -0x7ff6cff9:
        return (int)"OSS_BAD_VERSION";
      case -0x7ff6cff8:
        return (int)"OSS_OUT_MEMORY";
      case -0x7ff6cff7:
        return (int)"OSS_PDU_MISMATCH";
      case -0x7ff6cff6:
        return (int)"OSS_LIMITED";
      case -0x7ff6cff5:
        return (int)"OSS_BAD_PTR";
      case -0x7ff6cff4:
        return (int)"OSS_BAD_TIME";
      case -0x7ff6cff3:
        return (int)"OSS_INDEFINITE_NOT_SUPPORTED";
      case -0x7ff6cff2:
        return (int)"OSS_MEM_ERROR";
      case -0x7ff6cff1:
        return (int)"OSS_BAD_TABLE";
      case -0x7ff6cff0:
        return (int)"OSS_TOO_LONG";
      case -0x7ff6cfef:
        return (int)"OSS_CONSTRAINT_VIOLATED";
      case -0x7ff6cfee:
        return (int)"OSS_FATAL_ERROR";
      case -0x7ff6cfed:
        return (int)"OSS_ACCESS_SERIALIZATION_ERROR";
      case -0x7ff6cfec:
        return (int)"OSS_NULL_TBL";
      case -0x7ff6cfeb:
        return (int)"OSS_NULL_FCN";
      case -0x7ff6cfea:
        return (int)"OSS_BAD_ENCRULES";
      case -0x7ff6cfe9:
        return (int)"OSS_UNAVAIL_ENCRULES";
      case -0x7ff6cfe8:
        return (int)"OSS_CANT_OPEN_TRACE_WINDOW";
      case -0x7ff6cfe7:
        return (int)"OSS_UNIMPLEMENTED";
      case -0x7ff6cfe6:
        return (int)"OSS_OID_DLL_NOT_LINKED";
      case -0x7ff6cfe5:
        return (int)"OSS_CANT_OPEN_TRACE_FILE";
      case -0x7ff6cfe4:
        return (int)"OSS_TRACE_FILE_ALREADY_OPEN";
      case -0x7ff6cfe3:
        return (int)"OSS_TABLE_MISMATCH";
      case -0x7ff6cfe2:
        return (int)"OSS_TYPE_NOT_SUPPORTED";
      case -0x7ff6cfe1:
        return (int)"OSS_REAL_DLL_NOT_LINKED";
      case -0x7ff6cfe0:
        return (int)"OSS_REAL_CODE_NOT_LINKED";
      case -0x7ff6cfdf:
        return (int)"OSS_OUT_OF_RANGE";
      case -0x7ff6cfde:
        return (int)"OSS_COPIER_DLL_NOT_LINKED";
      case -0x7ff6cfdd:
        return (int)"OSS_CONSTRAINT_DLL_NOT_LINKED";
      case -0x7ff6cfdc:
        return (int)"OSS_COMPARATOR_DLL_NOT_LINKED";
      case -0x7ff6cfdb:
        return (int)"OSS_COMPARATOR_CODE_NOT_LINKED";
      case -0x7ff6cfda:
        return (int)"OSS_MEM_MGR_DLL_NOT_LINKED";
      case -0x7ff6cfd9:
        return (int)"OSS_PDV_DLL_NOT_LINKED";
      case -0x7ff6cfd8:
        return (int)"OSS_PDV_CODE_NOT_LINKED";
      case -0x7ff6cfd7:
        return (int)"OSS_API_DLL_NOT_LINKED";
      case -0x7ff6cfd6:
        return (int)"OSS_BERDER_DLL_NOT_LINKED";
      case -0x7ff6cfd5:
        return (int)"OSS_PER_DLL_NOT_LINKED";
      case -0x7ff6cfd4:
        return (int)"OSS_OPEN_TYPE_ERROR";
      case -0x7ff6cfd3:
        return (int)"OSS_MUTEX_NOT_CREATED";
      case -0x7ff6cfd2:
        return (int)"OSS_CANT_CLOSE_TRACE_FILE";
      }
    }
    else if (in_stack_00000004 < -0x7ff6cecc) {
      if (in_stack_00000004 == -0x7ff6cecd) {
        return (int)"CRYPT_E_ASN1_PDU_TYPE";
      }
      switch(in_stack_00000004) {
      case -0x7ff6ceff:
        return (int)"CRYPT_E_ASN1_INTERNAL";
      case -0x7ff6cefe:
        return (int)"CRYPT_E_ASN1_EOD";
      case -0x7ff6cefd:
        return (int)"CRYPT_E_ASN1_CORRUPT";
      case -0x7ff6cefc:
        return (int)"CRYPT_E_ASN1_LARGE";
      case -0x7ff6cefb:
        return (int)"CRYPT_E_ASN1_CONSTRAINT";
      case -0x7ff6cefa:
        return (int)"CRYPT_E_ASN1_MEMORY";
      case -0x7ff6cef9:
        return (int)"CRYPT_E_ASN1_OVERFLOW";
      case -0x7ff6cef8:
        return (int)"CRYPT_E_ASN1_BADPDU";
      case -0x7ff6cef7:
        return (int)"CRYPT_E_ASN1_BADARGS";
      case -0x7ff6cef6:
        return (int)"CRYPT_E_ASN1_BADREAL";
      case -0x7ff6cef5:
        return (int)"CRYPT_E_ASN1_BADTAG";
      case -0x7ff6cef4:
        return (int)"CRYPT_E_ASN1_CHOICE";
      case -0x7ff6cef3:
        return (int)"CRYPT_E_ASN1_RULE";
      case -0x7ff6cef2:
        return (int)"CRYPT_E_ASN1_UTF8";
      }
    }
    else if (in_stack_00000004 < -0x7ff6b7fd) {
      if (in_stack_00000004 == -0x7ff6b7fe) {
        return (int)"CERTSRV_E_TEMPLATE_CONFLICT";
      }
      if (in_stack_00000004 < -0x7ff6bff5) {
        if (in_stack_00000004 == -0x7ff6bff6) {
          return (int)"CERTSRV_E_KEY_ARCHIVAL_NOT_CONFIGURED";
        }
        if (in_stack_00000004 < -0x7ff6bffb) {
          if (in_stack_00000004 == -0x7ff6bffc) {
            return (int)"CERTSRV_E_PROPERTY_EMPTY";
          }
          if (in_stack_00000004 == -0x7ff6cecc) {
            return (int)"CRYPT_E_ASN1_NYI";
          }
          if (in_stack_00000004 == -0x7ff6cdff) {
            return (int)"CRYPT_E_ASN1_EXTENDED";
          }
          if (in_stack_00000004 == -0x7ff6cdfe) {
            return (int)"CRYPT_E_ASN1_NOEOD";
          }
          if (in_stack_00000004 == -0x7ff6bfff) {
            return (int)"CERTSRV_E_BAD_REQUESTSUBJECT";
          }
          if (in_stack_00000004 == -0x7ff6bffe) {
            return (int)"CERTSRV_E_NO_REQUEST";
          }
          if (in_stack_00000004 == -0x7ff6bffd) {
            return (int)"CERTSRV_E_BAD_REQUESTSTATUS";
          }
        }
        else {
          if (in_stack_00000004 == -0x7ff6bffb) {
            return (int)"CERTSRV_E_INVALID_CA_CERTIFICATE";
          }
          if (in_stack_00000004 == -0x7ff6bffa) {
            return (int)"CERTSRV_E_SERVER_SUSPENDED";
          }
          if (in_stack_00000004 == -0x7ff6bff9) {
            return (int)"CERTSRV_E_ENCODING_LENGTH";
          }
          if (in_stack_00000004 == -0x7ff6bff8) {
            return (int)"CERTSRV_E_ROLECONFLICT";
          }
          if (in_stack_00000004 == -0x7ff6bff7) {
            return (int)"CERTSRV_E_RESTRICTEDOFFICER";
          }
        }
      }
      else if (in_stack_00000004 < -0x7ff6b7ff) {
        if (in_stack_00000004 == -0x7ff6b800) {
          return (int)"CERTSRV_E_UNSUPPORTED_CERT_TYPE";
        }
        switch(in_stack_00000004) {
        case -0x7ff6bff5:
          return (int)"CERTSRV_E_NO_VALID_KRA";
        case -0x7ff6bff4:
          return (int)"CERTSRV_E_BAD_REQUEST_KEY_ARCHIVAL";
        case -0x7ff6bff3:
          return (int)"CERTSRV_E_NO_CAADMIN_DEFINED";
        case -0x7ff6bff2:
          return (int)"CERTSRV_E_BAD_RENEWAL_CERT_ATTRIBUTE";
        case -0x7ff6bff1:
          return (int)"CERTSRV_E_NO_DB_SESSIONS";
        case -0x7ff6bff0:
          return (int)"CERTSRV_E_ALIGNMENT_FAULT";
        case -0x7ff6bfef:
          return (int)"CERTSRV_E_ENROLL_DENIED";
        case -0x7ff6bfee:
          return (int)"CERTSRV_E_TEMPLATE_DENIED";
        case -0x7ff6bfed:
          return (int)"CERTSRV_E_DOWNLEVEL_DC_SSL_OR_UPGRADE";
        }
      }
      else if (in_stack_00000004 == -0x7ff6b7ff) {
        return (int)"CERTSRV_E_NO_CERT_TYPE";
      }
    }
    else if (in_stack_00000004 < -0x7ff6afff) {
      if (in_stack_00000004 == -0x7ff6b000) {
        return (int)"XENROLL_E_KEY_NOT_EXPORTABLE";
      }
      switch(in_stack_00000004) {
      case -0x7ff6b7fd:
        return (int)"CERTSRV_E_SUBJECT_ALT_NAME_REQUIRED";
      case -0x7ff6b7fc:
        return (int)"CERTSRV_E_ARCHIVED_KEY_REQUIRED";
      case -0x7ff6b7fb:
        return (int)"CERTSRV_E_SMIME_REQUIRED";
      case -0x7ff6b7fa:
        return (int)"CERTSRV_E_BAD_RENEWAL_SUBJECT";
      case -0x7ff6b7f9:
        return (int)"CERTSRV_E_BAD_TEMPLATE_VERSION";
      case -0x7ff6b7f8:
        return (int)"CERTSRV_E_TEMPLATE_POLICY_REQUIRED";
      case -0x7ff6b7f7:
        return (int)"CERTSRV_E_SIGNATURE_POLICY_REQUIRED";
      case -0x7ff6b7f6:
        return (int)"CERTSRV_E_SIGNATURE_COUNT";
      case -0x7ff6b7f5:
        return (int)"CERTSRV_E_SIGNATURE_REJECTED";
      case -0x7ff6b7f4:
        return (int)"CERTSRV_E_ISSUANCE_POLICY_REQUIRED";
      case -0x7ff6b7f3:
        return (int)"CERTSRV_E_SUBJECT_UPN_REQUIRED";
      case -0x7ff6b7f2:
        return (int)"CERTSRV_E_SUBJECT_DIRECTORY_GUID_REQUIRED";
      case -0x7ff6b7f1:
        return (int)"CERTSRV_E_SUBJECT_DNS_REQUIRED";
      case -0x7ff6b7f0:
        return (int)"CERTSRV_E_ARCHIVED_KEY_UNEXPECTED";
      case -0x7ff6b7ef:
        return (int)"CERTSRV_E_KEY_LENGTH";
      case -0x7ff6b7ee:
        return (int)"CERTSRV_E_SUBJECT_EMAIL_REQUIRED";
      case -0x7ff6b7ed:
        return (int)"CERTSRV_E_UNKNOWN_CERT_TYPE";
      case -0x7ff6b7ec:
        return (int)"CERTSRV_E_CERT_TYPE_OVERLAP";
      }
    }
    else {
      if (in_stack_00000004 == -0x7ff6afff) {
        return (int)"XENROLL_E_CANNOT_ADD_ROOT_CERT";
      }
      if (in_stack_00000004 == -0x7ff6affe) {
        return (int)"XENROLL_E_RESPONSE_KA_HASH_NOT_FOUND";
      }
      if (in_stack_00000004 == -0x7ff6affd) {
        return (int)"XENROLL_E_RESPONSE_UNEXPECTED_KA_HASH";
      }
      if (in_stack_00000004 == -0x7ff6affc) {
        return (int)"XENROLL_E_RESPONSE_KA_HASH_MISMATCH";
      }
      if (in_stack_00000004 == -0x7ff6affb) {
        return (int)"XENROLL_E_KEYSPEC_SMIME_MISMATCH";
      }
    }
  }
  else if (in_stack_00000004 < 0x6aa) {
    if (in_stack_00000004 == 0x6a9) {
switchD_005c061b_caseD_800706a9:
      return (int)"RPC_S_INVALID_STRING_UUID";
    }
    if (in_stack_00000004 < -0x7787edfc) {
      if (in_stack_00000004 == -0x7787edfd) {
        return (int)"DMUS_E_SEGMENT_INIT_FAILED";
      }
      if (in_stack_00000004 < -0x7feafe78) {
        if (in_stack_00000004 == -0x7feafe79) {
          return (int)"DVERR_INITIALIZED";
        }
        if (in_stack_00000004 < -0x7fefffd7) {
          if (in_stack_00000004 == -0x7fefffd8) {
            return (int)"SCARD_E_WRITE_TOO_MANY";
          }
          if (in_stack_00000004 < -0x7ff0fdf1) {
            if (in_stack_00000004 == -0x7ff0fdf2) {
              return (int)"SPAPI_E_DI_DO_DEFAULT";
            }
            if (in_stack_00000004 < -0x7ff4fefe) {
              if (in_stack_00000004 == -0x7ff4feff) {
                return (int)"CERT_E_EXPIRED";
              }
              if (in_stack_00000004 < -0x7ff68fef) {
                if (in_stack_00000004 == -0x7ff68ff0) {
                  return (int)"MSSIPOTF_E_FAILED_POLICY";
                }
                if (in_stack_00000004 < -0x7ff68ffb) {
                  if (in_stack_00000004 == -0x7ff68ffc) {
                    return (int)"MSSIPOTF_E_BAD_MAGICNUMBER";
                  }
                  if (in_stack_00000004 < -0x7ff69fe6) {
                    if (in_stack_00000004 == -0x7ff69fe7) {
                      return (int)"TRUST_E_BASIC_CONSTRAINTS";
                    }
                    if (in_stack_00000004 == -0x7ff69ffe) {
                      return (int)"TRUST_E_NO_SIGNER_CERT";
                    }
                    if (in_stack_00000004 == -0x7ff69ffd) {
                      return (int)"TRUST_E_COUNTER_SIGNER";
                    }
                    if (in_stack_00000004 == -0x7ff69ffc) {
                      return (int)"TRUST_E_CERT_SIGNATURE";
                    }
                    if (in_stack_00000004 == -0x7ff69ffb) {
                      return (int)"TRUST_E_TIME_STAMP";
                    }
                    if (in_stack_00000004 == -0x7ff69ff0) {
                      return (int)"TRUST_E_BAD_DIGEST";
                    }
                  }
                  else {
                    if (in_stack_00000004 == -0x7ff69fe2) {
                      return (int)"TRUST_E_FINANCIAL_CRITERIA";
                    }
                    if (in_stack_00000004 == -0x7ff68fff) {
                      return (int)"MSSIPOTF_E_OUTOFMEMRANGE";
                    }
                    if (in_stack_00000004 == -0x7ff68ffe) {
                      return (int)"MSSIPOTF_E_CANTGETOBJECT";
                    }
                    if (in_stack_00000004 == -0x7ff68ffd) {
                      return (int)"MSSIPOTF_E_NOHEADTABLE";
                    }
                  }
                }
                else {
                  switch(in_stack_00000004) {
                  case -0x7ff68ffb:
                    return (int)"MSSIPOTF_E_BAD_OFFSET_TABLE";
                  case -0x7ff68ffa:
                    return (int)"MSSIPOTF_E_TABLE_TAGORDER";
                  case -0x7ff68ff9:
                    return (int)"MSSIPOTF_E_TABLE_LONGWORD";
                  case -0x7ff68ff8:
                    return (int)"MSSIPOTF_E_BAD_FIRST_TABLE_PLACEMENT";
                  case -0x7ff68ff7:
                    return (int)"MSSIPOTF_E_TABLES_OVERLAP";
                  case -0x7ff68ff6:
                    return (int)"MSSIPOTF_E_TABLE_PADBYTES";
                  case -0x7ff68ff5:
                    return (int)"MSSIPOTF_E_FILETOOSMALL";
                  case -0x7ff68ff4:
                    return (int)"MSSIPOTF_E_TABLE_CHECKSUM";
                  case -0x7ff68ff3:
                    return (int)"MSSIPOTF_E_FILE_CHECKSUM";
                  }
                }
              }
              else if (in_stack_00000004 < -0x7ff4fffc) {
                if (in_stack_00000004 == -0x7ff4fffd) {
                  return (int)"TRUST_E_SUBJECT_FORM_UNKNOWN";
                }
                if (in_stack_00000004 < -0x7ff68fe9) {
                  if (in_stack_00000004 == -0x7ff68fea) {
                    return (int)"MSSIPOTF_E_DSIG_STRUCTURE";
                  }
                  if (in_stack_00000004 == -0x7ff68fef) {
                    return (int)"MSSIPOTF_E_FAILED_HINTS_CHECK";
                  }
                  if (in_stack_00000004 == -0x7ff68fee) {
                    return (int)"MSSIPOTF_E_NOT_OPENTYPE";
                  }
                  if (in_stack_00000004 == -0x7ff68fed) {
                    return (int)"MSSIPOTF_E_FILE";
                  }
                  if (in_stack_00000004 == -0x7ff68fec) {
                    return (int)"MSSIPOTF_E_CRYPT";
                  }
                  if (in_stack_00000004 == -0x7ff68feb) {
                    return (int)"MSSIPOTF_E_BADVERSION";
                  }
                }
                else {
                  if (in_stack_00000004 == -0x7ff68fe9) {
                    return (int)"MSSIPOTF_E_PCONST_CHECK";
                  }
                  if (in_stack_00000004 == -0x7ff68fe8) {
                    return (int)"MSSIPOTF_E_STRUCTURE";
                  }
                  if (in_stack_00000004 == -0x7ff4ffff) {
                    return (int)"TRUST_E_PROVIDER_UNKNOWN";
                  }
                  if (in_stack_00000004 == -0x7ff4fffe) {
                    return (int)"TRUST_E_ACTION_UNKNOWN";
                  }
                }
              }
              else if (in_stack_00000004 < -0x7ff4fff7) {
                if (in_stack_00000004 == -0x7ff4fff8) {
                  return (int)"DIGSIG_E_CRYPTO";
                }
                if (in_stack_00000004 == -0x7ff4fffc) {
                  return (int)"TRUST_E_SUBJECT_NOT_TRUSTED";
                }
                if (in_stack_00000004 == -0x7ff4fffb) {
                  return (int)"DIGSIG_E_ENCODE";
                }
                if (in_stack_00000004 == -0x7ff4fffa) {
                  return (int)"DIGSIG_E_DECODE";
                }
                if (in_stack_00000004 == -0x7ff4fff9) {
                  return (int)"DIGSIG_E_EXTENSIBILITY";
                }
              }
              else {
                if (in_stack_00000004 == -0x7ff4fff7) {
                  return (int)"PERSIST_E_SIZEDEFINITE";
                }
                if (in_stack_00000004 == -0x7ff4fff6) {
                  return (int)"PERSIST_E_SIZEINDEFINITE";
                }
                if (in_stack_00000004 == -0x7ff4fff5) {
                  return (int)"PERSIST_E_NOTSELFSIZING";
                }
                if (in_stack_00000004 == -0x7ff4ff00) {
                  return (int)"TRUST_E_NOSIGNATURE";
                }
              }
            }
            else if (in_stack_00000004 < -0x7ff0ffff) {
              if (in_stack_00000004 == -0x7ff10000) {
                return (int)"SPAPI_E_EXPECTED_SECTION_NAME";
              }
              switch(in_stack_00000004) {
              case -0x7ff4fefe:
                return (int)"CERT_E_VALIDITYPERIODNESTING";
              case -0x7ff4fefd:
                return (int)"CERT_E_ROLE";
              case -0x7ff4fefc:
                return (int)"CERT_E_PATHLENCONST";
              case -0x7ff4fefb:
                return (int)"CERT_E_CRITICAL";
              case -0x7ff4fefa:
                return (int)"CERT_E_PURPOSE";
              case -0x7ff4fef9:
                return (int)"CERT_E_ISSUERCHAINING";
              case -0x7ff4fef8:
                return (int)"CERT_E_MALFORMED";
              case -0x7ff4fef7:
                return (int)"CERT_E_UNTRUSTEDROOT";
              case -0x7ff4fef6:
                return (int)"CERT_E_CHAINING";
              case -0x7ff4fef5:
                return (int)"TRUST_E_FAIL";
              case -0x7ff4fef4:
                return (int)"CERT_E_REVOKED";
              case -0x7ff4fef3:
                return (int)"CERT_E_UNTRUSTEDTESTROOT";
              case -0x7ff4fef2:
                return (int)"CERT_E_REVOCATION_FAILURE";
              case -0x7ff4fef1:
                return (int)"CERT_E_CN_NO_MATCH";
              case -0x7ff4fef0:
                return (int)"CERT_E_WRONG_USAGE";
              case -0x7ff4feef:
                return (int)"TRUST_E_EXPLICIT_DISTRUST";
              case -0x7ff4feee:
                return (int)"CERT_E_UNTRUSTEDCA";
              case -0x7ff4feed:
                return (int)"CERT_E_INVALID_POLICY";
              case -0x7ff4feec:
                return (int)"CERT_E_INVALID_NAME";
              }
            }
            else if (in_stack_00000004 < -0x7ff0fdfc) {
              if (in_stack_00000004 == -0x7ff0fdfd) {
                return (int)"SPAPI_E_NO_DRIVER_SELECTED";
              }
              if (in_stack_00000004 < -0x7ff0fefd) {
                if (in_stack_00000004 == -0x7ff0fefe) {
                  return (int)"SPAPI_E_LINE_NOT_FOUND";
                }
                if (in_stack_00000004 == -0x7ff0ffff) {
                  return (int)"SPAPI_E_BAD_SECTION_NAME_LINE";
                }
                if (in_stack_00000004 == -0x7ff0fffe) {
                  return (int)"SPAPI_E_SECTION_NAME_TOO_LONG";
                }
                if (in_stack_00000004 == -0x7ff0fffd) {
                  return (int)"SPAPI_E_GENERAL_SYNTAX";
                }
                if (in_stack_00000004 == -0x7ff0ff00) {
                  return (int)"SPAPI_E_WRONG_INF_STYLE";
                }
                if (in_stack_00000004 == -0x7ff0feff) {
                  return (int)"SPAPI_E_SECTION_NOT_FOUND";
                }
              }
              else {
                if (in_stack_00000004 == -0x7ff0fefd) {
                  return (int)"SPAPI_E_NO_BACKUP";
                }
                if (in_stack_00000004 == -0x7ff0fe00) {
                  return (int)"SPAPI_E_NO_ASSOCIATED_CLASS";
                }
                if (in_stack_00000004 == -0x7ff0fdff) {
                  return (int)"SPAPI_E_CLASS_MISMATCH";
                }
                if (in_stack_00000004 == -0x7ff0fdfe) {
                  return (int)"SPAPI_E_DUPLICATE_FOUND";
                }
              }
            }
            else {
              switch(in_stack_00000004) {
              case -0x7ff0fdfc:
                return (int)"SPAPI_E_KEY_DOES_NOT_EXIST";
              case -0x7ff0fdfb:
                return (int)"SPAPI_E_INVALID_DEVINST_NAME";
              case -0x7ff0fdfa:
                return (int)"SPAPI_E_INVALID_CLASS";
              case -0x7ff0fdf9:
                return (int)"SPAPI_E_DEVINST_ALREADY_EXISTS";
              case -0x7ff0fdf8:
                return (int)"SPAPI_E_DEVINFO_NOT_REGISTERED";
              case -0x7ff0fdf7:
                return (int)"SPAPI_E_INVALID_REG_PROPERTY";
              case -0x7ff0fdf6:
                return (int)"SPAPI_E_NO_INF";
              case -0x7ff0fdf5:
                return (int)"SPAPI_E_NO_SUCH_DEVINST";
              case -0x7ff0fdf4:
                return (int)"SPAPI_E_CANT_LOAD_CLASS_ICON";
              case -0x7ff0fdf3:
                return (int)"SPAPI_E_INVALID_CLASS_INSTALLER";
              }
            }
          }
          else if (in_stack_00000004 < -0x7ff0efff) {
            if (in_stack_00000004 == -0x7ff0f000) {
              return (int)"SPAPI_E_ERROR_NOT_INSTALLED";
            }
            switch(in_stack_00000004) {
            case -0x7ff0fdf1:
              return (int)"SPAPI_E_DI_NOFILECOPY";
            case -0x7ff0fdf0:
              return (int)"SPAPI_E_INVALID_HWPROFILE";
            case -0x7ff0fdef:
              return (int)"SPAPI_E_NO_DEVICE_SELECTED";
            case -0x7ff0fdee:
              return (int)"SPAPI_E_DEVINFO_LIST_LOCKED";
            case -0x7ff0fded:
              return (int)"SPAPI_E_DEVINFO_DATA_LOCKED";
            case -0x7ff0fdec:
              return (int)"SPAPI_E_DI_BAD_PATH";
            case -0x7ff0fdeb:
              return (int)"SPAPI_E_NO_CLASSINSTALL_PARAMS";
            case -0x7ff0fdea:
              return (int)"SPAPI_E_FILEQUEUE_LOCKED";
            case -0x7ff0fde9:
              return (int)"SPAPI_E_BAD_SERVICE_INSTALLSECT";
            case -0x7ff0fde8:
              return (int)"SPAPI_E_NO_CLASS_DRIVER_LIST";
            case -0x7ff0fde7:
              return (int)"SPAPI_E_NO_ASSOCIATED_SERVICE";
            case -0x7ff0fde6:
              return (int)"SPAPI_E_NO_DEFAULT_DEVICE_INTERFACE";
            case -0x7ff0fde5:
              return (int)"SPAPI_E_DEVICE_INTERFACE_ACTIVE";
            case -0x7ff0fde4:
              return (int)"SPAPI_E_DEVICE_INTERFACE_REMOVED";
            case -0x7ff0fde3:
              return (int)"SPAPI_E_BAD_INTERFACE_INSTALLSECT";
            case -0x7ff0fde2:
              return (int)"SPAPI_E_NO_SUCH_INTERFACE_CLASS";
            case -0x7ff0fde1:
              return (int)"SPAPI_E_INVALID_REFERENCE_STRING";
            case -0x7ff0fde0:
              return (int)"SPAPI_E_INVALID_MACHINENAME";
            case -0x7ff0fddf:
              return (int)"SPAPI_E_REMOTE_COMM_FAILURE";
            case -0x7ff0fdde:
              return (int)"SPAPI_E_MACHINE_UNAVAILABLE";
            case -0x7ff0fddd:
              return (int)"SPAPI_E_NO_CONFIGMGR_SERVICES";
            case -0x7ff0fddc:
              return (int)"SPAPI_E_INVALID_PROPPAGE_PROVIDER";
            case -0x7ff0fddb:
              return (int)"SPAPI_E_NO_SUCH_DEVICE_INTERFACE";
            case -0x7ff0fdda:
              return (int)"SPAPI_E_DI_POSTPROCESSING_REQUIRED";
            case -0x7ff0fdd9:
              return (int)"SPAPI_E_INVALID_COINSTALLER";
            case -0x7ff0fdd8:
              return (int)"SPAPI_E_NO_COMPAT_DRIVERS";
            case -0x7ff0fdd7:
              return (int)"SPAPI_E_NO_DEVICE_ICON";
            case -0x7ff0fdd6:
              return (int)"SPAPI_E_INVALID_INF_LOGCONFIG";
            case -0x7ff0fdd5:
              return (int)&DAT_0060604c;
            case -0x7ff0fdd4:
              return (int)"SPAPI_E_INVALID_FILTER_DRIVER";
            case -0x7ff0fdd3:
              return (int)"SPAPI_E_NON_WINDOWS_NT_DRIVER";
            case -0x7ff0fdd2:
              return (int)"SPAPI_E_NON_WINDOWS_DRIVER";
            case -0x7ff0fdd1:
              return (int)"SPAPI_E_NO_CATALOG_FOR_OEM_INF";
            case -0x7ff0fdd0:
              return (int)"SPAPI_E_DEVINSTALL_QUEUE_NONNATIVE";
            case -0x7ff0fdcf:
              return (int)"SPAPI_E_NOT_DISABLEABLE";
            case -0x7ff0fdce:
              return (int)"SPAPI_E_CANT_REMOVE_DEVINST";
            case -0x7ff0fdcd:
              return (int)"SPAPI_E_INVALID_TARGET";
            case -0x7ff0fdcc:
              return (int)"SPAPI_E_DRIVER_NONNATIVE";
            case -0x7ff0fdcb:
              return (int)"SPAPI_E_IN_WOW64";
            case -0x7ff0fdca:
              return (int)"SPAPI_E_SET_SYSTEM_RESTORE_POINT";
            case -0x7ff0fdc9:
              return (int)"SPAPI_E_INCORRECTLY_COPIED_INF";
            case -0x7ff0fdc8:
              return (int)"SPAPI_E_SCE_DISABLED";
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7fefffff:
              return (int)"SCARD_F_INTERNAL_ERROR";
            case -0x7feffffe:
              return (int)"SCARD_E_CANCELLED";
            case -0x7feffffd:
              return (int)"SCARD_E_INVALID_HANDLE";
            case -0x7feffffc:
              return (int)"SCARD_E_INVALID_PARAMETER";
            case -0x7feffffb:
              return (int)"SCARD_E_INVALID_TARGET";
            case -0x7feffffa:
              return (int)"SCARD_E_NO_MEMORY";
            case -0x7feffff9:
              return (int)"SCARD_F_WAITED_TOO_LONG";
            case -0x7feffff8:
              return (int)"SCARD_E_INSUFFICIENT_BUFFER";
            case -0x7feffff7:
              return (int)"SCARD_E_UNKNOWN_READER";
            case -0x7feffff6:
              return (int)"SCARD_E_TIMEOUT";
            case -0x7feffff5:
              return (int)"SCARD_E_SHARING_VIOLATION";
            case -0x7feffff4:
              return (int)"SCARD_E_NO_SMARTCARD";
            case -0x7feffff3:
              return (int)"SCARD_E_UNKNOWN_CARD";
            case -0x7feffff2:
              return (int)"SCARD_E_CANT_DISPOSE";
            case -0x7feffff1:
              return (int)"SCARD_E_PROTO_MISMATCH";
            case -0x7feffff0:
              return (int)"SCARD_E_NOT_READY";
            case -0x7fefffef:
              return (int)"SCARD_E_INVALID_VALUE";
            case -0x7fefffee:
              return (int)"SCARD_E_SYSTEM_CANCELLED";
            case -0x7fefffed:
              return (int)"SCARD_F_COMM_ERROR";
            case -0x7fefffec:
              return (int)"SCARD_F_UNKNOWN_ERROR";
            case -0x7fefffeb:
              return (int)"SCARD_E_INVALID_ATR";
            case -0x7fefffea:
              return (int)"SCARD_E_NOT_TRANSACTED";
            case -0x7fefffe9:
              return (int)"SCARD_E_READER_UNAVAILABLE";
            case -0x7fefffe8:
              return (int)"SCARD_P_SHUTDOWN";
            case -0x7fefffe7:
              return (int)"SCARD_E_PCI_TOO_SMALL";
            case -0x7fefffe6:
              return (int)"SCARD_E_READER_UNSUPPORTED";
            case -0x7fefffe5:
              return (int)"SCARD_E_DUPLICATE_READER";
            case -0x7fefffe4:
              return (int)"SCARD_E_CARD_UNSUPPORTED";
            case -0x7fefffe3:
              return (int)"SCARD_E_NO_SERVICE";
            case -0x7fefffe2:
              return (int)"SCARD_E_SERVICE_STOPPED";
            case -0x7fefffe1:
              return (int)"SCARD_E_UNEXPECTED";
            case -0x7fefffe0:
              return (int)"SCARD_E_ICC_INSTALLATION";
            case -0x7fefffdf:
              return (int)"SCARD_E_ICC_CREATEORDER";
            case -0x7fefffde:
              return (int)"SCARD_E_UNSUPPORTED_FEATURE";
            case -0x7fefffdd:
              return (int)"SCARD_E_DIR_NOT_FOUND";
            case -0x7fefffdc:
              return (int)"SCARD_E_FILE_NOT_FOUND";
            case -0x7fefffdb:
              return (int)"SCARD_E_NO_DIR";
            case -0x7fefffda:
              return (int)"SCARD_E_NO_FILE";
            case -0x7fefffd9:
              return (int)"SCARD_E_NO_ACCESS";
            }
          }
        }
        else if (in_stack_00000004 < -0x7feefba5) {
          if (in_stack_00000004 == -0x7feefba6) {
            return (int)"COMADMIN_E_FILE_PARTITION_DUPLICATE_FILES";
          }
          if (in_stack_00000004 < -0x7feefbe1) {
            if (in_stack_00000004 == -0x7feefbe2) {
              return (int)"COMADMIN_E_BADREGISTRYLIBID";
            }
            if (in_stack_00000004 < -0x7feefbfd) {
              if (in_stack_00000004 == -0x7feefbfe) {
                return (int)"COMADMIN_E_OBJECTINVALID";
              }
              if (in_stack_00000004 < -0x7fefff98) {
                if (in_stack_00000004 == -0x7fefff99) {
                  return (int)"SCARD_W_UNPOWERED_CARD";
                }
                if (in_stack_00000004 < -0x7fefffd1) {
                  if (in_stack_00000004 == -0x7fefffd2) {
                    return (int)"SCARD_E_NO_READERS_AVAILABLE";
                  }
                  if (in_stack_00000004 == -0x7fefffd7) {
                    return (int)"SCARD_E_BAD_SEEK";
                  }
                  if (in_stack_00000004 == -0x7fefffd6) {
                    return (int)"SCARD_E_INVALID_CHV";
                  }
                  if (in_stack_00000004 == -0x7fefffd5) {
                    return (int)"SCARD_E_UNKNOWN_RES_MNG";
                  }
                  if (in_stack_00000004 == -0x7fefffd4) {
                    return (int)"SCARD_E_NO_SUCH_CERTIFICATE";
                  }
                  if (in_stack_00000004 == -0x7fefffd3) {
                    return (int)"SCARD_E_CERTIFICATE_UNAVAILABLE";
                  }
                }
                else {
                  if (in_stack_00000004 == -0x7fefffd1) {
                    return (int)"SCARD_E_COMM_DATA_LOST";
                  }
                  if (in_stack_00000004 == -0x7fefffd0) {
                    return (int)"SCARD_E_NO_KEY_CONTAINER";
                  }
                  if (in_stack_00000004 == -0x7fefff9b) {
                    return (int)"SCARD_W_UNSUPPORTED_CARD";
                  }
                  if (in_stack_00000004 == -0x7fefff9a) {
                    return (int)"SCARD_W_UNRESPONSIVE_CARD";
                  }
                }
              }
              else if (in_stack_00000004 < -0x7fefff93) {
                if (in_stack_00000004 == -0x7fefff94) {
                  return (int)"SCARD_W_CHV_BLOCKED";
                }
                if (in_stack_00000004 == -0x7fefff98) {
                  return (int)"SCARD_W_RESET_CARD";
                }
                if (in_stack_00000004 == -0x7fefff97) {
                  return (int)"SCARD_W_REMOVED_CARD";
                }
                if (in_stack_00000004 == -0x7fefff96) {
                  return (int)"SCARD_W_SECURITY_VIOLATION";
                }
                if (in_stack_00000004 == -0x7fefff95) {
                  return (int)"SCARD_W_WRONG_CHV";
                }
              }
              else {
                if (in_stack_00000004 == -0x7fefff93) {
                  return (int)"SCARD_W_EOF";
                }
                if (in_stack_00000004 == -0x7fefff92) {
                  return (int)"SCARD_W_CANCELLED_BY_USER";
                }
                if (in_stack_00000004 == -0x7fefff91) {
                  return (int)"SCARD_W_CARD_NOT_AUTHENTICATED";
                }
                if (in_stack_00000004 == -0x7feefbff) {
                  return (int)"COMADMIN_E_OBJECTERRORS";
                }
              }
            }
            else {
              switch(in_stack_00000004) {
              case -0x7feefbfd:
                return (int)"COMADMIN_E_KEYMISSING";
              case -0x7feefbfc:
                return (int)"COMADMIN_E_ALREADYINSTALLED";
              case -0x7feefbf9:
                return (int)"COMADMIN_E_APP_FILE_WRITEFAIL";
              case -0x7feefbf8:
                return (int)"COMADMIN_E_APP_FILE_READFAIL";
              case -0x7feefbf7:
                return (int)"COMADMIN_E_APP_FILE_VERSION";
              case -0x7feefbf6:
                return (int)"COMADMIN_E_BADPATH";
              case -0x7feefbf5:
                return (int)"COMADMIN_E_APPLICATIONEXISTS";
              case -0x7feefbf4:
                return (int)"COMADMIN_E_ROLEEXISTS";
              case -0x7feefbf3:
                return (int)"COMADMIN_E_CANTCOPYFILE";
              case -0x7feefbf1:
                return (int)"COMADMIN_E_NOUSER";
              case -0x7feefbf0:
                return (int)"COMADMIN_E_INVALIDUSERIDS";
              case -0x7feefbef:
                return (int)"COMADMIN_E_NOREGISTRYCLSID";
              case -0x7feefbee:
                return (int)"COMADMIN_E_BADREGISTRYPROGID";
              case -0x7feefbed:
                return (int)"COMADMIN_E_AUTHENTICATIONLEVEL";
              case -0x7feefbec:
                return (int)"COMADMIN_E_USERPASSWDNOTVALID";
              case -0x7feefbe8:
                return (int)"COMADMIN_E_CLSIDORIIDMISMATCH";
              case -0x7feefbe7:
                return (int)"COMADMIN_E_REMOTEINTERFACE";
              case -0x7feefbe6:
                return (int)"COMADMIN_E_DLLREGISTERSERVER";
              case -0x7feefbe5:
                return (int)"COMADMIN_E_NOSERVERSHARE";
              case -0x7feefbe3:
                return (int)"COMADMIN_E_DLLLOADFAILED";
              }
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7feefbe1:
              return (int)"COMADMIN_E_APPDIRNOTFOUND";
            case -0x7feefbdd:
              return (int)"COMADMIN_E_REGISTRARFAILED";
            case -0x7feefbdc:
              return (int)"COMADMIN_E_COMPFILE_DOESNOTEXIST";
            case -0x7feefbdb:
              return (int)"COMADMIN_E_COMPFILE_LOADDLLFAIL";
            case -0x7feefbda:
              return (int)"COMADMIN_E_COMPFILE_GETCLASSOBJ";
            case -0x7feefbd9:
              return (int)"COMADMIN_E_COMPFILE_CLASSNOTAVAIL";
            case -0x7feefbd8:
              return (int)"COMADMIN_E_COMPFILE_BADTLB";
            case -0x7feefbd7:
              return (int)"COMADMIN_E_COMPFILE_NOTINSTALLABLE";
            case -0x7feefbd6:
              return (int)"COMADMIN_E_NOTCHANGEABLE";
            case -0x7feefbd5:
              return (int)"COMADMIN_E_NOTDELETEABLE";
            case -0x7feefbd4:
              return (int)"COMADMIN_E_SESSION";
            case -0x7feefbd3:
              return (int)"COMADMIN_E_COMP_MOVE_LOCKED";
            case -0x7feefbd2:
              return (int)"COMADMIN_E_COMP_MOVE_BAD_DEST";
            case -0x7feefbd0:
              return (int)"COMADMIN_E_REGISTERTLB";
            case -0x7feefbcd:
              return (int)"COMADMIN_E_SYSTEMAPP";
            case -0x7feefbcc:
              return (int)"COMADMIN_E_COMPFILE_NOREGISTRAR";
            case -0x7feefbcb:
              return (int)"COMADMIN_E_COREQCOMPINSTALLED";
            case -0x7feefbca:
              return (int)"COMADMIN_E_SERVICENOTINSTALLED";
            case -0x7feefbc9:
              return (int)"COMADMIN_E_PROPERTYSAVEFAILED";
            case -0x7feefbc8:
              return (int)"COMADMIN_E_OBJECTEXISTS";
            case -0x7feefbc7:
              return (int)"COMADMIN_E_COMPONENTEXISTS";
            case -0x7feefbc5:
              return (int)"COMADMIN_E_REGFILE_CORRUPT";
            case -0x7feefbc4:
              return (int)"COMADMIN_E_PROPERTY_OVERFLOW";
            case -0x7feefbc2:
              return (int)"COMADMIN_E_NOTINREGISTRY";
            case -0x7feefbc1:
              return (int)"COMADMIN_E_OBJECTNOTPOOLABLE";
            case -0x7feefbba:
              return (int)"COMADMIN_E_APPLID_MATCHES_CLSID";
            case -0x7feefbb9:
              return (int)"COMADMIN_E_ROLE_DOES_NOT_EXIST";
            case -0x7feefbb8:
              return (int)"COMADMIN_E_START_APP_NEEDS_COMPONENTS";
            case -0x7feefbb7:
              return (int)"COMADMIN_E_REQUIRES_DIFFERENT_PLATFORM";
            case -0x7feefbb6:
              return (int)"COMADMIN_E_CAN_NOT_EXPORT_APP_PROXY";
            case -0x7feefbb5:
              return (int)"COMADMIN_E_CAN_NOT_START_APP";
            case -0x7feefbb4:
              return (int)"COMADMIN_E_CAN_NOT_EXPORT_SYS_APP";
            case -0x7feefbb3:
              return (int)"COMADMIN_E_CANT_SUBSCRIBE_TO_COMPONENT";
            case -0x7feefbb2:
              return (int)"COMADMIN_E_EVENTCLASS_CANT_BE_SUBSCRIBER";
            case -0x7feefbb1:
              return (int)"COMADMIN_E_LIB_APP_PROXY_INCOMPATIBLE";
            case -0x7feefbb0:
              return (int)"COMADMIN_E_BASE_PARTITION_ONLY";
            case -0x7feefbaf:
              return (int)"COMADMIN_E_START_APP_DISABLED";
            case -0x7feefba9:
              return (int)"COMADMIN_E_CAT_DUPLICATE_PARTITION_NAME";
            case -0x7feefba8:
              return (int)"COMADMIN_E_CAT_INVALID_PARTITION_NAME";
            case -0x7feefba7:
              return (int)"COMADMIN_E_CAT_PARTITION_IN_USE";
            }
          }
        }
        else if (in_stack_00000004 < -0x7feef7e2) {
          if (in_stack_00000004 == -0x7feef7e3) {
            return (int)"COMADMIN_E_COMP_MOVE_DEST";
          }
          if (in_stack_00000004 < -0x7feef9f9) {
            if (in_stack_00000004 == -0x7feef9fa) {
              return (int)"COMQC_E_UNTRUSTED_ENQUEUER";
            }
            if (in_stack_00000004 < -0x7feefb7c) {
              if (in_stack_00000004 == -0x7feefb7d) {
                return (int)"COMADMIN_E_CAT_UNACCEPTABLEBITNESS";
              }
              if (in_stack_00000004 < -0x7feefb8b) {
                if (in_stack_00000004 == -0x7feefb8c) {
                  return (int)"COMADMIN_E_REGDB_SYSTEMERR";
                }
                if (in_stack_00000004 == -0x7feefba5) {
                  return (int)"COMADMIN_E_CAT_IMPORTED_COMPONENTS_NOT_ALLOWED";
                }
                if (in_stack_00000004 == -0x7feefba4) {
                  return (int)"COMADMIN_E_AMBIGUOUS_APPLICATION_NAME";
                }
                if (in_stack_00000004 == -0x7feefba3) {
                  return (int)"COMADMIN_E_AMBIGUOUS_PARTITION_NAME";
                }
                if (in_stack_00000004 == -0x7feefb8e) {
                  return (int)"COMADMIN_E_REGDB_NOTINITIALIZED";
                }
                if (in_stack_00000004 == -0x7feefb8d) {
                  return (int)"COMADMIN_E_REGDB_NOTOPEN";
                }
              }
              else {
                if (in_stack_00000004 == -0x7feefb8b) {
                  return (int)"COMADMIN_E_REGDB_ALREADYRUNNING";
                }
                if (in_stack_00000004 == -0x7feefb80) {
                  return (int)"COMADMIN_E_MIG_VERSIONNOTSUPPORTED";
                }
                if (in_stack_00000004 == -0x7feefb7f) {
                  return (int)"COMADMIN_E_MIG_SCHEMANOTFOUND";
                }
                if (in_stack_00000004 == -0x7feefb7e) {
                  return (int)"COMADMIN_E_CAT_BITNESSMISMATCH";
                }
              }
            }
            else if (in_stack_00000004 < -0x7feef9fe) {
              if (in_stack_00000004 == -0x7feef9ff) {
                return (int)"COMQC_E_NO_QUEUEABLE_INTERFACES";
              }
              if (in_stack_00000004 == -0x7feefb7c) {
                return (int)"COMADMIN_E_CAT_WRONGAPPBITNESS";
              }
              if (in_stack_00000004 == -0x7feefb7b) {
                return (int)"COMADMIN_E_CAT_PAUSE_RESUME_NOT_SUPPORTED";
              }
              if (in_stack_00000004 == -0x7feefb7a) {
                return (int)"COMADMIN_E_CAT_SERVERFAULT";
              }
              if (in_stack_00000004 == -0x7feefa00) {
                return (int)"COMQC_E_APPLICATION_NOT_QUEUED";
              }
            }
            else {
              if (in_stack_00000004 == -0x7feef9fe) {
                return (int)"COMQC_E_QUEUING_SERVICE_NOT_AVAILABLE";
              }
              if (in_stack_00000004 == -0x7feef9fd) {
                return (int)"COMQC_E_NO_IPERSISTSTREAM";
              }
              if (in_stack_00000004 == -0x7feef9fc) {
                return (int)"COMQC_E_BAD_MESSAGE";
              }
              if (in_stack_00000004 == -0x7feef9fb) {
                return (int)"COMQC_E_UNAUTHENTICATED";
              }
            }
          }
          else if (in_stack_00000004 < -0x7feef7ec) {
            if (in_stack_00000004 == -0x7feef7ed) {
              return (int)"COMADMIN_E_PAUSEDPROCESSMAYNOTBERECYCLED";
            }
            if (in_stack_00000004 < -0x7feef7f2) {
              if (in_stack_00000004 == -0x7feef7f3) {
                return (int)"COMADMIN_E_SVCAPP_NOT_POOLABLE_OR_RECYCLABLE";
              }
              if (in_stack_00000004 == -0x7feef8ff) {
                return (int)"MSDTC_E_DUPLICATE_RESOURCE";
              }
              if (in_stack_00000004 == -0x7feef7f8) {
                return (int)"COMADMIN_E_OBJECT_PARENT_MISSING";
              }
              if (in_stack_00000004 == -0x7feef7f7) {
                return (int)"COMADMIN_E_OBJECT_DOES_NOT_EXIST";
              }
              if (in_stack_00000004 == -0x7feef7f6) {
                return (int)"COMADMIN_E_APP_NOT_RUNNING";
              }
              if (in_stack_00000004 == -0x7feef7f5) {
                return (int)"COMADMIN_E_INVALID_PARTITION";
              }
            }
            else {
              if (in_stack_00000004 == -0x7feef7f2) {
                return (int)"COMADMIN_E_USER_IN_SET";
              }
              if (in_stack_00000004 == -0x7feef7f1) {
                return (int)"COMADMIN_E_CANTRECYCLELIBRARYAPPS";
              }
              if (in_stack_00000004 == -0x7feef7ef) {
                return (int)"COMADMIN_E_CANTRECYCLESERVICEAPPS";
              }
              if (in_stack_00000004 == -0x7feef7ee) {
                return (int)"COMADMIN_E_PROCESSALREADYRECYCLED";
              }
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7feef7ec:
              return (int)"COMADMIN_E_CANTMAKEINPROCSERVICE";
            case -0x7feef7eb:
              return (int)"COMADMIN_E_PROGIDINUSEBYCLSID";
            case -0x7feef7ea:
              return (int)"COMADMIN_E_DEFAULT_PARTITION_NOT_IN_SET";
            case -0x7feef7e9:
              return (int)"COMADMIN_E_RECYCLEDPROCESSMAYNOTBEPAUSED";
            case -0x7feef7e8:
              return (int)"COMADMIN_E_PARTITION_ACCESSDENIED";
            case -0x7feef7e7:
              return (int)"COMADMIN_E_PARTITION_MSI_ONLY";
            case -0x7feef7e6:
              return (int)"COMADMIN_E_LEGACYCOMPS_NOT_ALLOWED_IN_1_0_FORMAT";
            case -0x7feef7e5:
              return (int)"COMADMIN_E_LEGACYCOMPS_NOT_ALLOWED_IN_NONBASE_PARTITIONS";
            case -0x7feef7e4:
              return (int)"COMADMIN_E_COMP_MOVE_SOURCE";
            }
          }
        }
        else if (in_stack_00000004 < -0x7feafe90) {
          if (in_stack_00000004 == -0x7feafe91) {
            return (int)"DVERR_NOTALLOWED";
          }
          if (in_stack_00000004 < -0x7feaff78) {
            if (in_stack_00000004 == -0x7feaff79) {
              return (int)"DVERR_INVALIDPLAYER";
            }
            if (in_stack_00000004 < -0x7feef7dc) {
              if (in_stack_00000004 == -0x7feef7dd) {
                return (int)"COMADMIN_E_REGISTRY_ACCESSDENIED";
              }
              if (in_stack_00000004 == -0x7feef7e2) {
                return (int)"COMADMIN_E_COMP_MOVE_PRIVATE";
              }
              if (in_stack_00000004 == -0x7feef7e1) {
                return (int)"COMADMIN_E_BASEPARTITION_REQUIRED_IN_SET";
              }
              if (in_stack_00000004 == -0x7feef7e0) {
                return (int)"COMADMIN_E_CANNOT_ALIAS_EVENTCLASS";
              }
              if (in_stack_00000004 == -0x7feef7df) {
                return (int)"COMADMIN_E_PRIVATE_ACCESSDENIED";
              }
              if (in_stack_00000004 == -0x7feef7de) {
                return (int)"COMADMIN_E_SAFERINVALID";
              }
            }
            else {
              if (in_stack_00000004 == -0x7feaffe2) {
                return (int)"DVERR_BUFFERTOOSMALL";
              }
              if (in_stack_00000004 == -0x7feaffb6) {
                return (int)"DVERR_EXCEPTION";
              }
              if (in_stack_00000004 == -0x7feaff88) {
                return (int)"DVERR_INVALIDFLAGS";
              }
              if (in_stack_00000004 == -0x7feaff7e) {
                return (int)"DVERR_INVALIDOBJECT";
              }
            }
          }
          else if (in_stack_00000004 < -0x7feafe97) {
            if (in_stack_00000004 == -0x7feafe98) {
              return (int)"DVERR_CONNECTIONLOST";
            }
            if (in_stack_00000004 == -0x7feaff6f) {
              return (int)"DVERR_INVALIDGROUP";
            }
            if (in_stack_00000004 == -0x7feaff6a) {
              return (int)"DVERR_INVALIDHANDLE";
            }
            if (in_stack_00000004 == -0x7feafed4) {
              return (int)"DVERR_SESSIONLOST";
            }
            if (in_stack_00000004 == -0x7feafed2) {
              return (int)"DVERR_NOVOICESESSION";
            }
          }
          else {
            if (in_stack_00000004 == -0x7feafe97) {
              return (int)"DVERR_NOTINITIALIZED";
            }
            if (in_stack_00000004 == -0x7feafe96) {
              return (int)"DVERR_CONNECTED";
            }
            if (in_stack_00000004 == -0x7feafe95) {
              return (int)"DVERR_NOTCONNECTED";
            }
            if (in_stack_00000004 == -0x7feafe92) {
              return (int)"DVERR_CONNECTABORTING";
            }
          }
        }
        else {
          switch(in_stack_00000004) {
          case -0x7feafe90:
            return (int)"DVERR_INVALIDTARGET";
          case -0x7feafe8f:
            return (int)"DVERR_TRANSPORTNOTHOST";
          case -0x7feafe8e:
            return (int)"DVERR_COMPRESSIONNOTSUPPORTED";
          case -0x7feafe8d:
            return (int)"DVERR_ALREADYPENDING";
          case -0x7feafe8c:
            return (int)"DVERR_SOUNDINITFAILURE";
          case -0x7feafe8b:
            return (int)"DVERR_TIMEOUT";
          case -0x7feafe8a:
            return (int)"DVERR_CONNECTABORTED";
          case -0x7feafe89:
            return (int)"DVERR_NO3DSOUND";
          case -0x7feafe88:
            return (int)"DVERR_ALREADYBUFFERED";
          case -0x7feafe87:
            return (int)"DVERR_NOTBUFFERED";
          case -0x7feafe86:
            return (int)"DVERR_HOSTING";
          case -0x7feafe85:
            return (int)"DVERR_NOTHOSTING";
          case -0x7feafe84:
            return (int)"DVERR_INVALIDDEVICE";
          case -0x7feafe83:
            return (int)"DVERR_RECORDSYSTEMERROR";
          case -0x7feafe82:
            return (int)"DVERR_PLAYBACKSYSTEMERROR";
          case -0x7feafe81:
            return (int)"DVERR_SENDERROR";
          case -0x7feafe80:
            return (int)"DVERR_USERCANCEL";
          case -0x7feafe7d:
            return (int)"DVERR_RUNSETUP";
          case -0x7feafe7c:
            return (int)"DVERR_INCOMPATIBLEVERSION";
          }
        }
      }
      else if (in_stack_00000004 < -0x7fea7fcf) {
        if (in_stack_00000004 == -0x7fea7fd0) {
          return (int)"DPNERR_ABORTED";
        }
        switch(in_stack_00000004) {
        case -0x7feafe78:
          return (int)"DVERR_NOTRANSPORT";
        case -0x7feafe77:
          return (int)"DVERR_NOCALLBACK";
        case -0x7feafe76:
          return (int)"DVERR_TRANSPORTNOTINIT";
        case -0x7feafe75:
          return (int)"DVERR_TRANSPORTNOSESSION";
        case -0x7feafe74:
          return (int)"DVERR_TRANSPORTNOPLAYER";
        case -0x7feafe73:
          return (int)"DVERR_USERBACK";
        case -0x7feafe72:
          return (int)"DVERR_NORECVOLAVAILABLE";
        case -0x7feafe71:
          return (int)"DVERR_INVALIDBUFFER";
        case -0x7feafe70:
          return (int)"DVERR_LOCKEDBUFFER";
        }
      }
      else if (in_stack_00000004 < -0x7789fda7) {
        if (in_stack_00000004 == -0x7789fda8) {
          return (int)"DDERR_NOOPTIMIZEHW";
        }
        if (in_stack_00000004 < -0x7789ff4a) {
          if (in_stack_00000004 == -0x7789ff4b) {
            return (int)"DDERR_NOSTEREOHARDWARE";
          }
          if (in_stack_00000004 < -0x7fea7bdf) {
            if (in_stack_00000004 == -0x7fea7be0) {
              return (int)"DPNERR_INVALIDPLAYER";
            }
            if (in_stack_00000004 < -0x7fea7ddf) {
              if (in_stack_00000004 == -0x7fea7de0) {
                return (int)"DPNERR_ENUMRESPONSETOOLARGE";
              }
              if (in_stack_00000004 < -0x7fea7ebf) {
                if (in_stack_00000004 == -0x7fea7ec0) {
                  return (int)"DPNERR_CANTLAUNCHAPPLICATION";
                }
                if (in_stack_00000004 < -0x7fea7f6f) {
                  if (in_stack_00000004 == -0x7fea7f70) {
                    return (int)"DPNERR_ALREADYREGISTERED";
                  }
                  if (in_stack_00000004 == -0x7fea7fc0) {
                    return (int)"DPNERR_ADDRESSING";
                  }
                  if (in_stack_00000004 == -0x7fea7fb0) {
                    return (int)"DPNERR_ALREADYCLOSING";
                  }
                  if (in_stack_00000004 == -0x7fea7fa0) {
                    return (int)"DPNERR_ALREADYCONNECTED";
                  }
                  if (in_stack_00000004 == -0x7fea7f90) {
                    return (int)"DPNERR_ALREADYDISCONNECTING";
                  }
                  if (in_stack_00000004 == -0x7fea7f80) {
                    return (int)"DPNERR_ALREADYINITIALIZED";
                  }
                }
                else {
                  if (in_stack_00000004 == -0x7fea7f00) {
                    return (int)"DPNERR_BUFFERTOOSMALL";
                  }
                  if (in_stack_00000004 == -0x7fea7ef0) {
                    return (int)"DPNERR_CANNOTCANCEL";
                  }
                  if (in_stack_00000004 == -0x7fea7ee0) {
                    return (int)"DPNERR_CANTCREATEGROUP";
                  }
                  if (in_stack_00000004 == -0x7fea7ed0) {
                    return (int)"DPNERR_CANTCREATEPLAYER";
                  }
                }
              }
              else if (in_stack_00000004 < -0x7fea7e7f) {
                if (in_stack_00000004 == -0x7fea7e80) {
                  return (int)"DPNERR_DOESNOTEXIST";
                }
                if (in_stack_00000004 == -0x7fea7eb0) {
                  return (int)"DPNERR_CONNECTING";
                }
                if (in_stack_00000004 == -0x7fea7ea0) {
                  return (int)"DPNERR_CONNECTIONLOST";
                }
                if (in_stack_00000004 == -0x7fea7e90) {
                  return (int)"DPNERR_CONVERSION";
                }
                if (in_stack_00000004 == -0x7fea7e8b) {
                  return (int)"DPNERR_DATATOOLARGE";
                }
              }
              else {
                if (in_stack_00000004 == -0x7fea7e7b) {
                  return (int)"DPNERR_DPNSVRNOTAVAILABLE";
                }
                if (in_stack_00000004 == -0x7fea7e70) {
                  return (int)"DPNERR_DUPLICATECOMMAND";
                }
                if (in_stack_00000004 == -0x7fea7e00) {
                  return (int)"DPNERR_ENDPOINTNOTRECEIVING";
                }
                if (in_stack_00000004 == -0x7fea7df0) {
                  return (int)"DPNERR_ENUMQUERYTOOLARGE";
                }
              }
            }
            else if (in_stack_00000004 < -0x7fea7cdf) {
              if (in_stack_00000004 == -0x7fea7ce0) {
                return (int)"DPNERR_INVALIDDEVICEADDRESS";
              }
              if (in_stack_00000004 < -0x7fea7d8f) {
                if (in_stack_00000004 == -0x7fea7d90) {
                  return (int)"DPNERR_HOSTTERMINATEDSESSION";
                }
                if (in_stack_00000004 == -0x7fea7dd0) {
                  return (int)"DPNERR_EXCEPTION";
                }
                if (in_stack_00000004 == -0x7fea7dc0) {
                  return (int)"DPNERR_GROUPNOTEMPTY";
                }
                if (in_stack_00000004 == -0x7fea7db0) {
                  return (int)"DPNERR_HOSTING";
                }
                if (in_stack_00000004 == -0x7fea7da0) {
                  return (int)"DPNERR_HOSTREJECTEDCONNECTION";
                }
              }
              else {
                if (in_stack_00000004 == -0x7fea7d80) {
                  return (int)"DPNERR_INCOMPLETEADDRESS";
                }
                if (in_stack_00000004 == -0x7fea7d70) {
                  return (int)"DPNERR_INVALIDADDRESSFORMAT";
                }
                if (in_stack_00000004 == -0x7fea7d00) {
                  return (int)"DPNERR_INVALIDAPPLICATION";
                }
                if (in_stack_00000004 == -0x7fea7cf0) {
                  return (int)"DPNERR_INVALIDCOMMAND";
                }
              }
            }
            else if (in_stack_00000004 < -0x7fea7c8f) {
              if (in_stack_00000004 == -0x7fea7c90) {
                return (int)"DPNERR_INVALIDHOSTADDRESS";
              }
              if (in_stack_00000004 == -0x7fea7cd0) {
                return (int)"DPNERR_INVALIDENDPOINT";
              }
              if (in_stack_00000004 == -0x7fea7cc0) {
                return (int)"DPNERR_INVALIDFLAGS";
              }
              if (in_stack_00000004 == -0x7fea7cb0) {
                return (int)"DPNERR_INVALIDGROUP";
              }
              if (in_stack_00000004 == -0x7fea7ca0) {
                return (int)"DPNERR_INVALIDHANDLE";
              }
            }
            else {
              if (in_stack_00000004 == -0x7fea7c80) {
                return (int)"DPNERR_INVALIDINSTANCE";
              }
              if (in_stack_00000004 == -0x7fea7c70) {
                return (int)"DPNERR_INVALIDINTERFACE";
              }
              if (in_stack_00000004 == -0x7fea7c00) {
                return (int)"DPNERR_INVALIDOBJECT";
              }
              if (in_stack_00000004 == -0x7fea7bf0) {
                return (int)"DPNERR_INVALIDPASSWORD";
              }
            }
          }
          else if (in_stack_00000004 < -0x7fea79df) {
            if (in_stack_00000004 == -0x7fea79e0) {
              return (int)"DPNERR_TABLEFULL";
            }
            if (in_stack_00000004 < -0x7fea7adf) {
              if (in_stack_00000004 == -0x7fea7ae0) {
                return (int)"DPNERR_NOTALLOWED";
              }
              if (in_stack_00000004 < -0x7fea7b8f) {
                if (in_stack_00000004 == -0x7fea7b90) {
                  return (int)"DPNERR_NOCAPS";
                }
                if (in_stack_00000004 == -0x7fea7bd0) {
                  return (int)"DPNERR_INVALIDPRIORITY";
                }
                if (in_stack_00000004 == -0x7fea7bc0) {
                  return (int)"DPNERR_INVALIDSTRING";
                }
                if (in_stack_00000004 == -0x7fea7bb0) {
                  return (int)"DPNERR_INVALIDURL";
                }
                if (in_stack_00000004 == -0x7fea7ba0) {
                  return (int)"DPNERR_INVALIDVERSION";
                }
              }
              else {
                if (in_stack_00000004 == -0x7fea7b80) {
                  return (int)"DPNERR_NOCONNECTION";
                }
                if (in_stack_00000004 == -0x7fea7b70) {
                  return (int)"DPNERR_NOHOSTPLAYER";
                }
                if (in_stack_00000004 == -0x7fea7b00) {
                  return (int)"DPNERR_NOMOREADDRESSCOMPONENTS";
                }
                if (in_stack_00000004 == -0x7fea7af0) {
                  return (int)"DPNERR_NORESPONSE";
                }
              }
            }
            else if (in_stack_00000004 < -0x7fea7a8f) {
              if (in_stack_00000004 == -0x7fea7a90) {
                return (int)"DPNERR_PLAYERLOST";
              }
              if (in_stack_00000004 == -0x7fea7ad0) {
                return (int)"DPNERR_NOTHOST";
              }
              if (in_stack_00000004 == -0x7fea7ac0) {
                return (int)"DPNERR_NOTREADY";
              }
              if (in_stack_00000004 == -0x7fea7ab0) {
                return (int)"DPNERR_NOTREGISTERED";
              }
              if (in_stack_00000004 == -0x7fea7aa0) {
                return (int)"DPNERR_PLAYERALREADYINGROUP";
              }
            }
            else {
              if (in_stack_00000004 == -0x7fea7a80) {
                return (int)"DPNERR_PLAYERNOTINGROUP";
              }
              if (in_stack_00000004 == -0x7fea7a70) {
                return (int)"DPNERR_PLAYERNOTREACHABLE";
              }
              if (in_stack_00000004 == -0x7fea7a00) {
                return (int)"DPNERR_SENDTOOLARGE";
              }
              if (in_stack_00000004 == -0x7fea79f0) {
                return (int)"DPNERR_SESSIONFULL";
              }
            }
          }
          else if (in_stack_00000004 < -0x7789ffa0) {
            if (in_stack_00000004 == -0x7789ffa1) {
              return (int)"DDERR_INCOMPATIBLEPRIMARY";
            }
            if (in_stack_00000004 < -0x7789fff5) {
              if (in_stack_00000004 == -0x7789fff6) {
                return (int)"DDERR_CANNOTATTACHSURFACE";
              }
              if (in_stack_00000004 == -0x7fea79d0) {
                return (int)"DPNERR_TIMEDOUT";
              }
              if (in_stack_00000004 == -0x7fea79c0) {
                return (int)"DPNERR_UNINITIALIZED";
              }
              if (in_stack_00000004 == -0x7fea79b0) {
                return (int)"DPNERR_USERCANCEL";
              }
              if (in_stack_00000004 == -0x7789fffb) {
                return (int)"DDERR_ALREADYINITIALIZED";
              }
            }
            else {
              if (in_stack_00000004 == -0x7789ffec) {
                return (int)"DDERR_CANNOTDETACHSURFACE";
              }
              if (in_stack_00000004 == -0x7789ffd8) {
                return (int)"DDERR_CURRENTLYNOTAVAIL";
              }
              if (in_stack_00000004 == -0x7789ffc9) {
                return (int)"DDERR_EXCEPTION";
              }
              if (in_stack_00000004 == -0x7789ffa6) {
                return (int)"DDERR_HEIGHTALIGN";
              }
            }
          }
          else if (in_stack_00000004 < -0x7789ff6e) {
            if (in_stack_00000004 == -0x7789ff6f) {
              return (int)"DDERR_INVALIDPIXELFORMAT";
            }
            if (in_stack_00000004 == -0x7789ff9c) {
              return (int)"DDERR_INVALIDCAPS";
            }
            if (in_stack_00000004 == -0x7789ff92) {
              return (int)"DDERR_INVALIDCLIPLIST";
            }
            if (in_stack_00000004 == -0x7789ff88) {
              return (int)"DDERR_INVALIDMODE";
            }
            if (in_stack_00000004 == -0x7789ff7e) {
              return (int)"DDERR_INVALIDOBJECT";
            }
          }
          else {
            if (in_stack_00000004 == -0x7789ff6a) {
              return (int)"DDERR_INVALIDRECT";
            }
            if (in_stack_00000004 == -0x7789ff60) {
              return (int)"DDERR_LOCKEDSURFACES";
            }
            if (in_stack_00000004 == -0x7789ff56) {
              return (int)"DDERR_NO3D";
            }
            if (in_stack_00000004 == -0x7789ff4c) {
              return (int)"DDERR_NOALPHAHW";
            }
          }
        }
        else if (in_stack_00000004 < -0x7789fe15) {
          if (in_stack_00000004 == -0x7789fe16) {
            return (int)"DDERR_TOOBIGWIDTH";
          }
          if (in_stack_00000004 < -0x7789febf) {
            if (in_stack_00000004 == -0x7789fec0) {
              return (int)"DDERR_NOT8BITCOLOR";
            }
            if (in_stack_00000004 < -0x7789ff0f) {
              if (in_stack_00000004 == -0x7789ff10) {
                return (int)"DDERR_NOGDI";
              }
              if (in_stack_00000004 < -0x7789ff28) {
                if (in_stack_00000004 == -0x7789ff29) {
                  return (int)"DDERR_NOCOLORKEY";
                }
                if (in_stack_00000004 == -0x7789ff4a) {
                  return (int)"DDERR_NOSURFACELEFT";
                }
                if (in_stack_00000004 == -0x7789ff33) {
                  return (int)"DDERR_NOCLIPLIST";
                }
                if (in_stack_00000004 == -0x7789ff2e) {
                  return (int)"DDERR_NOCOLORCONVHW";
                }
                if (in_stack_00000004 == -0x7789ff2c) {
                  return (int)"DDERR_NOCOOPERATIVELEVELSET";
                }
              }
              else {
                if (in_stack_00000004 == -0x7789ff24) {
                  return (int)"DDERR_NOCOLORKEYHW";
                }
                if (in_stack_00000004 == -0x7789ff22) {
                  return (int)"DDERR_NODIRECTDRAWSUPPORT";
                }
                if (in_stack_00000004 == -0x7789ff1f) {
                  return (int)"DDERR_NOEXCLUSIVEMODE";
                }
                if (in_stack_00000004 == -0x7789ff1a) {
                  return (int)"DDERR_NOFLIPHW";
                }
              }
            }
            else if (in_stack_00000004 < -0x7789fee7) {
              if (in_stack_00000004 == -0x7789fee8) {
                return (int)"DDERR_NORASTEROPHW";
              }
              if (in_stack_00000004 == -0x7789ff06) {
                return (int)"DDERR_NOMIRRORHW";
              }
              if (in_stack_00000004 == -0x7789ff01) {
                return (int)"DDERR_NOTFOUND";
              }
              if (in_stack_00000004 == -0x7789fefc) {
                return (int)"DDERR_NOOVERLAYHW";
              }
              if (in_stack_00000004 == -0x7789fef2) {
                return (int)"DDERR_OVERLAPPINGRECTS";
              }
            }
            else {
              if (in_stack_00000004 == -0x7789fede) {
                return (int)"DDERR_NOROTATIONHW";
              }
              if (in_stack_00000004 == -0x7789feca) {
                return (int)"DDERR_NOSTRETCHHW";
              }
              if (in_stack_00000004 == -0x7789fec4) {
                return (int)"DDERR_NOT4BITCOLOR";
              }
              if (in_stack_00000004 == -0x7789fec3) {
                return (int)"DDERR_NOT4BITCOLORINDEX";
              }
            }
          }
          else if (in_stack_00000004 < -0x7789fe6f) {
            if (in_stack_00000004 == -0x7789fe70) {
              return (int)"DDERR_COLORKEYNOTSET";
            }
            if (in_stack_00000004 < -0x7789fe97) {
              if (in_stack_00000004 == -0x7789fe98) {
                return (int)"DDERR_OUTOFCAPS";
              }
              if (in_stack_00000004 == -0x7789feb6) {
                return (int)"DDERR_NOTEXTUREHW";
              }
              if (in_stack_00000004 == -0x7789feb1) {
                return (int)"DDERR_NOVSYNCHW";
              }
              if (in_stack_00000004 == -0x7789feac) {
                return (int)"DDERR_NOZBUFFERHW";
              }
              if (in_stack_00000004 == -0x7789fea2) {
                return (int)"DDERR_NOZOVERLAYHW";
              }
            }
            else {
              if (in_stack_00000004 == -0x7789fe84) {
                return (int)"D3DERR_OUTOFVIDEOMEMORY";
              }
              if (in_stack_00000004 == -0x7789fe82) {
                return (int)"DDERR_OVERLAYCANTCLIP";
              }
              if (in_stack_00000004 == -0x7789fe80) {
                return (int)"DDERR_OVERLAYCOLORKEYONLYONEACTIVE";
              }
              if (in_stack_00000004 == -0x7789fe7d) {
                return (int)"DDERR_PALETTEBUSY";
              }
            }
          }
          else if (in_stack_00000004 < -0x7789fe47) {
            if (in_stack_00000004 == -0x7789fe48) {
              return (int)"DDERR_SURFACEISOBSCURED";
            }
            if (in_stack_00000004 == -0x7789fe66) {
              return (int)"DDERR_SURFACEALREADYATTACHED";
            }
            if (in_stack_00000004 == -0x7789fe5c) {
              return (int)"DDERR_SURFACEALREADYDEPENDENT";
            }
            if (in_stack_00000004 == -0x7789fe52) {
              return (int)"DDERR_SURFACEBUSY";
            }
            if (in_stack_00000004 == -0x7789fe4d) {
              return (int)"DDERR_CANTLOCKSURFACE";
            }
          }
          else {
            if (in_stack_00000004 == -0x7789fe3e) {
              return (int)"DDERR_SURFACELOST";
            }
            if (in_stack_00000004 == -0x7789fe34) {
              return (int)"DDERR_SURFACENOTATTACHED";
            }
            if (in_stack_00000004 == -0x7789fe2a) {
              return (int)"DDERR_TOOBIGHEIGHT";
            }
            if (in_stack_00000004 == -0x7789fe20) {
              return (int)"DDERR_TOOBIGSIZE";
            }
          }
        }
        else {
          switch(in_stack_00000004) {
          case -0x7789fe02:
            return (int)"DDERR_UNSUPPORTEDFORMAT";
          case -0x7789fdf8:
            return (int)"DDERR_UNSUPPORTEDMASK";
          case -0x7789fdf7:
            return (int)"DDERR_INVALIDSTREAM";
          case -0x7789fde7:
            return (int)"DDERR_VERTICALBLANKINPROGRESS";
          case -0x7789fde4:
            return (int)"DDERR_WASSTILLDRAWING";
          case -0x7789fde2:
            return (int)"DDERR_DDSCAPSCOMPLEXREQUIRED";
          case -0x7789fdd0:
            return (int)"DDERR_XALIGN";
          case -0x7789fdcf:
            return (int)"DDERR_INVALIDDIRECTDRAWGUID";
          case -0x7789fdce:
            return (int)"DDERR_DIRECTDRAWALREADYCREATED";
          case -0x7789fdcd:
            return (int)"DDERR_NODIRECTDRAWHW";
          case -0x7789fdcc:
            return (int)"DDERR_PRIMARYSURFACEALREADYEXISTS";
          case -0x7789fdcb:
            return (int)"DDERR_NOEMULATION";
          case -0x7789fdca:
            return (int)"DDERR_REGIONTOOSMALL";
          case -0x7789fdc9:
            return (int)"DDERR_CLIPPERISUSINGHWND";
          case -0x7789fdc8:
            return (int)"DDERR_NOCLIPPERATTACHED";
          case -0x7789fdc7:
            return (int)"DDERR_NOHWND";
          case -0x7789fdc6:
            return (int)"DDERR_HWNDSUBCLASSED";
          case -0x7789fdc5:
            return (int)"DDERR_HWNDALREADYSET";
          case -0x7789fdc4:
            return (int)"DDERR_NOPALETTEATTACHED";
          case -0x7789fdc3:
            return (int)"DDERR_NOPALETTEHW";
          case -0x7789fdc2:
            return (int)"DDERR_BLTFASTCANTCLIP";
          case -0x7789fdc1:
            return (int)"DDERR_NOBLTHW";
          case -0x7789fdc0:
            return (int)"DDERR_NODDROPSHW";
          case -0x7789fdbf:
            return (int)"DDERR_OVERLAYNOTVISIBLE";
          case -0x7789fdbe:
            return (int)"DDERR_NOOVERLAYDEST";
          case -0x7789fdbd:
            return (int)"DDERR_INVALIDPOSITION";
          case -0x7789fdbc:
            return (int)"DDERR_NOTAOVERLAYSURFACE";
          case -0x7789fdbb:
            return (int)"DDERR_EXCLUSIVEMODEALREADYSET";
          case -0x7789fdba:
            return (int)"DDERR_NOTFLIPPABLE";
          case -0x7789fdb9:
            return (int)"DDERR_CANTDUPLICATE";
          case -0x7789fdb8:
            return (int)"DDERR_NOTLOCKED";
          case -0x7789fdb7:
            return (int)"DDERR_CANTCREATEDC";
          case -0x7789fdb6:
            return (int)"DDERR_NODC";
          case -0x7789fdb5:
            return (int)"DDERR_WRONGMODE";
          case -0x7789fdb4:
            return (int)"DDERR_IMPLICITLYCREATED";
          case -0x7789fdb3:
            return (int)"DDERR_NOTPALETTIZED";
          case -0x7789fdb2:
            return (int)"DDERR_UNSUPPORTEDMODE";
          case -0x7789fdb1:
            return (int)"DDERR_NOMIPMAPHW";
          case -0x7789fdb0:
            return (int)"DDERR_INVALIDSURFACETYPE";
          }
        }
      }
      else if (in_stack_00000004 < -0x7787ff5f) {
        if (in_stack_00000004 == -0x7787ff60) {
          return (int)"DSERR_OTHERAPPHASPRIO";
        }
        if (in_stack_00000004 < -0x7789fc96) {
          if (in_stack_00000004 == -0x7789fc97) {
            return (int)"DXFILEERR_NOMORESTREAMHANDLES";
          }
          if (in_stack_00000004 < -0x7789fcaa) {
            if (in_stack_00000004 == -0x7789fcab) {
              return (int)"DXFILEERR_BADSTREAMHANDLE";
            }
            if (in_stack_00000004 < -0x7789fd4b) {
              if (in_stack_00000004 == -0x7789fd4c) {
                return (int)"DDERR_TESTFINISHED";
              }
              if (in_stack_00000004 < -0x7789fd7f) {
                if (in_stack_00000004 == -0x7789fd80) {
                  return (int)"DDERR_CANTPAGELOCK";
                }
                if (in_stack_00000004 == -0x7789fda7) {
                  return (int)"DDERR_NOTLOADED";
                }
                if (in_stack_00000004 == -0x7789fda6) {
                  return (int)"DDERR_NOFOCUSWINDOW";
                }
                if (in_stack_00000004 == -0x7789fda5) {
                  return (int)"DDERR_NOTONMIPMAPSUBLEVEL";
                }
                if (in_stack_00000004 == -0x7789fd94) {
                  return (int)"DDERR_DCALREADYCREATED";
                }
                if (in_stack_00000004 == -0x7789fd8a) {
                  return (int)"DDERR_NONONLOCALVIDMEM";
                }
              }
              else {
                if (in_stack_00000004 == -0x7789fd6c) {
                  return (int)"DDERR_CANTPAGEUNLOCK";
                }
                if (in_stack_00000004 == -0x7789fd58) {
                  return (int)"DDERR_NOTPAGELOCKED";
                }
                if (in_stack_00000004 == -0x7789fd4e) {
                  return (int)"DDERR_MOREDATA";
                }
                if (in_stack_00000004 == -0x7789fd4d) {
                  return (int)"DDERR_EXPIRED";
                }
              }
            }
            else if (in_stack_00000004 < -0x7789fd46) {
              if (in_stack_00000004 == -0x7789fd47) {
                return (int)"DDERR_NODRIVERSUPPORT";
              }
              if (in_stack_00000004 == -0x7789fd4b) {
                return (int)"DDERR_NEWMODE";
              }
              if (in_stack_00000004 == -0x7789fd4a) {
                return (int)"DDERR_D3DNOTINITIALIZED";
              }
              if (in_stack_00000004 == -0x7789fd49) {
                return (int)"DDERR_VIDEONOTACTIVE";
              }
              if (in_stack_00000004 == -0x7789fd48) {
                return (int)"DDERR_NOMONITORINFORMATION";
              }
            }
            else {
              if (in_stack_00000004 == -0x7789fd45) {
                return (int)"DDERR_DEVICEDOESNTOWNSURFACE";
              }
              if (in_stack_00000004 == -0x7789fcae) {
                return (int)"DXFILEERR_BADOBJECT";
              }
              if (in_stack_00000004 == -0x7789fcad) {
                return (int)"DXFILEERR_BADVALUE";
              }
              if (in_stack_00000004 == -0x7789fcac) {
                return (int)"DXFILEERR_BADTYPE";
              }
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7789fcaa:
              return (int)"DXFILEERR_BADALLOC";
            case -0x7789fca9:
              return (int)"DXFILEERR_NOTFOUND";
            case -0x7789fca8:
              return (int)"DXFILEERR_NOTDONEYET";
            case -0x7789fca7:
              return (int)"DXFILEERR_FILENOTFOUND";
            case -0x7789fca6:
              return (int)"DXFILEERR_RESOURCENOTFOUND";
            case -0x7789fca5:
              return (int)"DXFILEERR_URLNOTFOUND";
            case -0x7789fca4:
              return (int)"DXFILEERR_BADRESOURCE";
            case -0x7789fca3:
              return (int)"DXFILEERR_BADFILETYPE";
            case -0x7789fca2:
              return (int)"DXFILEERR_BADFILEVERSION";
            case -0x7789fca1:
              return (int)"DXFILEERR_BADFILEFLOATSIZE";
            case -0x7789fca0:
              return (int)"DXFILEERR_BADFILECOMPRESSIONTYPE";
            case -0x7789fc9f:
              return (int)"DXFILEERR_BADFILE";
            case -0x7789fc9e:
              return (int)"DXFILEERR_PARSEERROR";
            case -0x7789fc9d:
              return (int)"DXFILEERR_NOTEMPLATE";
            case -0x7789fc9c:
              return (int)"DXFILEERR_BADARRAYSIZE";
            case -0x7789fc9b:
              return (int)"DXFILEERR_BADDATAREFERENCE";
            case -0x7789fc9a:
              return (int)"DXFILEERR_INTERNALERROR";
            case -0x7789fc99:
              return (int)"DXFILEERR_NOMOREOBJECTS";
            case -0x7789fc98:
              return (int)"DXFILEERR_BADINTRINSICS";
            }
          }
        }
        else if (in_stack_00000004 < -0x7789f795) {
          if (in_stack_00000004 == -0x7789f796) {
            return (int)"D3DERR_NOTAVAILABLE";
          }
          if (in_stack_00000004 < -0x7789f7e1) {
            if (in_stack_00000004 == -0x7789f7e2) {
              return (int)"D3DERR_CONFLICTINGTEXTUREFILTER";
            }
            if (in_stack_00000004 < -0x7789f7e6) {
              if (in_stack_00000004 == -0x7789f7e7) {
                return (int)"D3DERR_UNSUPPORTEDCOLOROPERATION";
              }
              if (in_stack_00000004 == -0x7789fc96) {
                return (int)"DXFILEERR_NOMOREDATA";
              }
              if (in_stack_00000004 == -0x7789fc95) {
                return (int)"DXFILEERR_BADCACHEFILE";
              }
              if (in_stack_00000004 == -0x7789fc94) {
                return (int)"DXFILEERR_NOINTERNET";
              }
              if (in_stack_00000004 == -0x7789f7e8) {
                return (int)"D3DERR_WRONGTEXTUREFORMAT";
              }
            }
            else {
              if (in_stack_00000004 == -0x7789f7e6) {
                return (int)"D3DERR_UNSUPPORTEDCOLORARG";
              }
              if (in_stack_00000004 == -0x7789f7e5) {
                return (int)"D3DERR_UNSUPPORTEDALPHAOPERATION";
              }
              if (in_stack_00000004 == -0x7789f7e4) {
                return (int)"D3DERR_UNSUPPORTEDALPHAARG";
              }
              if (in_stack_00000004 == -0x7789f7e3) {
                return (int)"D3DERR_TOOMANYOPERATIONS";
              }
            }
          }
          else if (in_stack_00000004 < -0x7789f7d8) {
            if (in_stack_00000004 == -0x7789f7d9) {
              return (int)"D3DERR_DRIVERINTERNALERROR";
            }
            if (in_stack_00000004 == -0x7789f7e1) {
              return (int)"D3DERR_UNSUPPORTEDFACTORVALUE";
            }
            if (in_stack_00000004 == -0x7789f7df) {
              return (int)"D3DERR_CONFLICTINGRENDERSTATE";
            }
            if (in_stack_00000004 == -0x7789f7de) {
              return (int)"D3DERR_UNSUPPORTEDTEXTUREFILTER";
            }
            if (in_stack_00000004 == -0x7789f7da) {
              return (int)"D3DERR_CONFLICTINGTEXTUREPALETTE";
            }
          }
          else {
            if (in_stack_00000004 == -0x7789f79a) {
              return (int)"D3DERR_NOTFOUND";
            }
            if (in_stack_00000004 == -0x7789f799) {
              return (int)"D3DERR_MOREDATA";
            }
            if (in_stack_00000004 == -0x7789f798) {
              return (int)"D3DERR_DEVICELOST";
            }
            if (in_stack_00000004 == -0x7789f797) {
              return (int)"D3DERR_DEVICENOTRESET";
            }
          }
        }
        else if (in_stack_00000004 < -0x7789f4a5) {
          if (in_stack_00000004 == -0x7789f4a6) {
            return (int)"D3DXERR_LOADEDMESHASNODATA";
          }
          if (in_stack_00000004 < -0x7789f4aa) {
            if (in_stack_00000004 == -0x7789f4ab) {
              return (int)"D3DXERR_INVALIDMESH";
            }
            if (in_stack_00000004 == -0x7789f795) {
              return (int)"D3DERR_INVALIDDEVICE";
            }
            if (in_stack_00000004 == -0x7789f794) {
              return (int)"D3DERR_INVALIDCALL";
            }
            if (in_stack_00000004 == -0x7789f793) {
              return (int)"D3DERR_DRIVERINVALIDCALL";
            }
            if (in_stack_00000004 == -0x7789f4ac) {
              return (int)"D3DXERR_CANNOTMODIFYINDEXBUFFER";
            }
          }
          else {
            if (in_stack_00000004 == -0x7789f4aa) {
              return (int)"D3DXERR_CANNOTATTRSORT";
            }
            if (in_stack_00000004 == -0x7789f4a9) {
              return (int)"D3DXERR_SKINNINGNOTSUPPORTED";
            }
            if (in_stack_00000004 == -0x7789f4a8) {
              return (int)"D3DXERR_TOOMANYINFLUENCES";
            }
            if (in_stack_00000004 == -0x7789f4a7) {
              return (int)"D3DXERR_INVALIDDATA";
            }
          }
        }
        else if (in_stack_00000004 < -0x7787ffb9) {
          if (in_stack_00000004 == -0x7787ffba) {
            return (int)"DSERR_PRIOLEVELNEEDED";
          }
          if (in_stack_00000004 == -0x7789f4a5) {
            return (int)"D3DXERR_DUPLICATENAMEDFRAGMENT";
          }
          if (in_stack_00000004 == -0x7787fff6) {
            return (int)"DSERR_ALLOCATED";
          }
          if (in_stack_00000004 == -0x7787ffe2) {
            return (int)"DSERR_CONTROLUNAVAIL";
          }
          if (in_stack_00000004 == -0x7787ffce) {
            return (int)"DSERR_INVALIDCALL";
          }
        }
        else {
          if (in_stack_00000004 == -0x7787ff9c) {
            return (int)"DSERR_BADFORMAT";
          }
          if (in_stack_00000004 == -0x7787ff88) {
            return (int)"DSERR_NODRIVER";
          }
          if (in_stack_00000004 == -0x7787ff7e) {
            return (int)"DSERR_ALREADYINITIALIZED";
          }
          if (in_stack_00000004 == -0x7787ff6a) {
            return (int)"DSERR_BUFFERLOST";
          }
        }
      }
      else if (in_stack_00000004 < -0x7787eecc) {
        if (in_stack_00000004 == -0x7787eecd) {
          return (int)"DMUS_E_CANNOTREAD";
        }
        if (in_stack_00000004 < -0x7787eee6) {
          if (in_stack_00000004 == -0x7787eee7) {
            return (int)"DMUS_E_INVALID_DOWNLOADID";
          }
          if (in_stack_00000004 < -0x7787eefa) {
            if (in_stack_00000004 == -0x7787eefb) {
              return (int)"DMUS_E_BUFFERNOTSET";
            }
            if (in_stack_00000004 < -0x7787ff2d) {
              if (in_stack_00000004 == -0x7787ff2e) {
                return (int)"DSERR_BADSENDBUFFERGUID";
              }
              if (in_stack_00000004 == -0x7787ff56) {
                return (int)"DSERR_UNINITIALIZED";
              }
              if (in_stack_00000004 == -0x7787ff4c) {
                return (int)"DSERR_BUFFERTOOSMALL";
              }
              if (in_stack_00000004 == -0x7787ff42) {
                return (int)"DSERR_DS8_REQUIRED";
              }
              if (in_stack_00000004 == -0x7787ff38) {
                return (int)"DSERR_SENDLOOP";
              }
            }
            else {
              if (in_stack_00000004 == -0x7787eeff) {
                return (int)"DMUS_E_DRIVER_FAILED";
              }
              if (in_stack_00000004 == -0x7787eefe) {
                return (int)"DMUS_E_PORTS_OPEN";
              }
              if (in_stack_00000004 == -0x7787eefd) {
                return (int)"DMUS_E_DEVICE_IN_USE";
              }
              if (in_stack_00000004 == -0x7787eefc) {
                return (int)"DMUS_E_INSUFFICIENTBUFFER";
              }
            }
          }
          else {
            switch(in_stack_00000004) {
            case -0x7787eefa:
              return (int)"DMUS_E_BUFFERNOTAVAILABLE";
            case -0x7787eef8:
              return (int)"DMUS_E_NOTADLSCOL";
            case -0x7787eef7:
              return (int)"DMUS_E_INVALIDOFFSET";
            case -0x7787eeef:
              return (int)"DMUS_E_ALREADY_LOADED";
            case -0x7787eeed:
              return (int)"DMUS_E_INVALIDPOS";
            case -0x7787eeec:
              return (int)"DMUS_E_INVALIDPATCH";
            case -0x7787eeeb:
              return (int)"DMUS_E_CANNOTSEEK";
            case -0x7787eeea:
              return (int)"DMUS_E_CANNOTWRITE";
            case -0x7787eee9:
              return (int)"DMUS_E_CHUNKNOTFOUND";
            }
          }
        }
        else {
          switch(in_stack_00000004) {
          case -0x7787eee0:
            return (int)"DMUS_E_NOT_DOWNLOADED_TO_PORT";
          case -0x7787eedf:
            return (int)"DMUS_E_ALREADY_DOWNLOADED";
          case -0x7787eede:
            return (int)"DMUS_E_UNKNOWN_PROPERTY";
          case -0x7787eedd:
            return (int)"DMUS_E_SET_UNSUPPORTED";
          case -0x7787eedc:
            return (int)"DMUS_E_GET_UNSUPPORTED";
          case -0x7787eedb:
            return (int)"DMUS_E_NOTMONO";
          case -0x7787eeda:
            return (int)"DMUS_E_BADARTICULATION";
          case -0x7787eed9:
            return (int)"DMUS_E_BADINSTRUMENT";
          case -0x7787eed8:
            return (int)"DMUS_E_BADWAVELINK";
          case -0x7787eed7:
            return (int)"DMUS_E_NOARTICULATION";
          case -0x7787eed6:
            return (int)"DMUS_E_NOTPCM";
          case -0x7787eed5:
            return (int)"DMUS_E_BADWAVE";
          case -0x7787eed4:
            return (int)"DMUS_E_BADOFFSETTABLE";
          case -0x7787eed3:
            return (int)"DMUS_E_UNKNOWNDOWNLOAD";
          case -0x7787eed2:
            return (int)"DMUS_E_NOSYNTHSINK";
          case -0x7787eed1:
            return (int)"DMUS_E_ALREADYOPEN";
          case -0x7787eed0:
            return (int)"DMUS_E_ALREADYCLOSED";
          case -0x7787eecf:
            return (int)"DMUS_E_SYNTHNOTCONFIGURED";
          case -0x7787eece:
            return (int)"DMUS_E_SYNTHACTIVE";
          }
        }
      }
      else if (in_stack_00000004 < -0x7787ee8f) {
        if (in_stack_00000004 == -0x7787ee90) {
          return (int)"DMUS_E_NO_MASTER_CLOCK";
        }
        switch(in_stack_00000004) {
        case -0x7787eecc:
          return (int)"DMUS_E_DMUSIC_RELEASED";
        case -0x7787eecb:
          return (int)"DMUS_E_BUFFER_EMPTY";
        case -0x7787eeca:
          return (int)"DMUS_E_BUFFER_FULL";
        case -0x7787eec9:
          return (int)"DMUS_E_PORT_NOT_CAPTURE";
        case -0x7787eec8:
          return (int)"DMUS_E_PORT_NOT_RENDER";
        case -0x7787eec7:
          return (int)"DMUS_E_DSOUND_NOT_SET";
        case -0x7787eec6:
          return (int)"DMUS_E_ALREADY_ACTIVATED";
        case -0x7787eec5:
          return (int)"DMUS_E_INVALIDBUFFER";
        case -0x7787eec4:
          return (int)"DMUS_E_WAVEFORMATNOTSUPPORTED";
        case -0x7787eec3:
          return (int)"DMUS_E_SYNTHINACTIVE";
        case -0x7787eec2:
          return (int)"DMUS_E_DSOUND_ALREADY_SET";
        case -0x7787eec1:
          return (int)"DMUS_E_INVALID_EVENT";
        case -0x7787eeb0:
          return (int)"DMUS_E_UNSUPPORTED_STREAM";
        case -0x7787eeaf:
          return (int)"DMUS_E_ALREADY_INITED";
        case -0x7787eeae:
          return (int)"DMUS_E_INVALID_BAND";
        case -0x7787eeab:
          return (int)"DMUS_E_TRACK_HDR_NOT_FIRST_CK";
        case -0x7787eeaa:
          return (int)"DMUS_E_TOOL_HDR_NOT_FIRST_CK";
        case -0x7787eea9:
          return (int)"DMUS_E_INVALID_TRACK_HDR";
        case -0x7787eea8:
          return (int)"DMUS_E_INVALID_TOOL_HDR";
        case -0x7787eea7:
          return (int)"DMUS_E_ALL_TOOLS_FAILED";
        case -0x7787eea0:
          return (int)"DMUS_E_ALL_TRACKS_FAILED";
        case -0x7787ee9f:
          return (int)"DSERR_OBJECTNOTFOUND";
        case -0x7787ee9e:
          return (int)"DMUS_E_NOT_INIT";
        case -0x7787ee9d:
          return (int)"DMUS_E_TYPE_DISABLED";
        case -0x7787ee9c:
          return (int)"DMUS_E_TYPE_UNSUPPORTED";
        case -0x7787ee9b:
          return (int)"DMUS_E_TIME_PAST";
        case -0x7787ee9a:
          return (int)"DMUS_E_TRACK_NOT_FOUND";
        case -0x7787ee99:
          return (int)"DMUS_E_TRACK_NO_CLOCKTIME_SUPPORT";
        }
      }
      else if (in_stack_00000004 < -0x7787ee7a) {
        if (in_stack_00000004 == -0x7787ee7b) {
          return (int)"DMUS_E_LOADER_OBJECTNOTFOUND";
        }
        if (in_stack_00000004 == -0x7787ee80) {
          return (int)"DMUS_E_LOADER_NOCLASSID";
        }
        if (in_stack_00000004 == -0x7787ee7f) {
          return (int)"DMUS_E_LOADER_BADPATH";
        }
        if (in_stack_00000004 == -0x7787ee7e) {
          return (int)"DMUS_E_LOADER_FAILEDOPEN";
        }
        if (in_stack_00000004 == -0x7787ee7d) {
          return (int)"DMUS_E_LOADER_FORMATNOTSUPPORTED";
        }
        if (in_stack_00000004 == -0x7787ee7c) {
          return (int)"DMUS_E_LOADER_FAILEDCREATE";
        }
      }
      else {
        if (in_stack_00000004 == -0x7787ee7a) {
          return (int)"DMUS_E_LOADER_NOFILENAME";
        }
        if (in_stack_00000004 == -0x7787ee00) {
          return (int)"DMUS_E_INVALIDFILE";
        }
        if (in_stack_00000004 == -0x7787edff) {
          return (int)"DMUS_E_ALREADY_EXISTS";
        }
        if (in_stack_00000004 == -0x7787edfe) {
          return (int)"DMUS_E_OUT_OF_RANGE";
        }
      }
    }
    else if (in_stack_00000004 < 0x477) {
      if (in_stack_00000004 == 0x476) {
switchD_005c05ed_caseD_80070476:
        return (int)"ERROR_TOO_MANY_LINKS";
      }
      if (in_stack_00000004 < 0xa3) {
        if (in_stack_00000004 == 0xa2) goto switchD_005c04b1_caseD_800700a2;
        if (in_stack_00000004 < 0x3c) {
          if (in_stack_00000004 == 0x3b) {
switchD_005c047c_caseD_8007003b:
            return (int)"ERROR_UNEXP_NET_ERR";
          }
          if (in_stack_00000004 < 6) {
            if (in_stack_00000004 == 5) {
              return (int)"ERROR_ACCESS_DENIED";
            }
            if (in_stack_00000004 < -0x7787eddd) {
              if (in_stack_00000004 == -0x7787edde) {
                return (int)"DMUS_E_INVALID_PARAMCONTROLTRACK";
              }
              switch(in_stack_00000004) {
              case -0x7787edfc:
                return (int)"DMUS_E_ALREADY_SENT";
              case -0x7787edfb:
                return (int)"DMUS_E_CANNOT_FREE";
              case -0x7787edfa:
                return (int)"DMUS_E_CANNOT_OPEN_PORT";
              case -0x7787edf9:
                return (int)"DMUS_E_CANNOT_CONVERT";
              case -0x7787edf0:
                return (int)"DMUS_E_DESCEND_CHUNK_FAIL";
              case -0x7787edef:
                return (int)"DMUS_E_NOT_LOADED";
              case -0x7787eded:
                return (int)"DMUS_E_SCRIPT_LANGUAGE_INCOMPATIBLE";
              case -0x7787edec:
                return (int)"DMUS_E_SCRIPT_UNSUPPORTED_VARTYPE";
              case -0x7787edeb:
                return (int)"DMUS_E_SCRIPT_ERROR_IN_SCRIPT";
              case -0x7787edea:
                return (int)"DMUS_E_SCRIPT_CANTLOAD_OLEAUT32";
              case -0x7787ede9:
                return (int)"DMUS_E_SCRIPT_LOADSCRIPT_ERROR";
              case -0x7787ede8:
                return (int)"DMUS_E_SCRIPT_INVALID_FILE";
              case -0x7787ede7:
                return (int)"DMUS_E_INVALID_SCRIPTTRACK";
              case -0x7787ede6:
                return (int)"DMUS_E_SCRIPT_VARIABLE_NOT_FOUND";
              case -0x7787ede5:
                return (int)"DMUS_E_SCRIPT_ROUTINE_NOT_FOUND";
              case -0x7787ede4:
                return (int)"DMUS_E_SCRIPT_CONTENT_READONLY";
              case -0x7787ede3:
                return (int)"DMUS_E_SCRIPT_NOT_A_REFERENCE";
              case -0x7787ede2:
                return (int)"DMUS_E_SCRIPT_VALUE_NOT_SUPPORTED";
              case -0x7787ede0:
                return (int)"DMUS_E_INVALID_SEGMENTTRIGGERTRACK";
              case -0x7787eddf:
                return (int)"DMUS_E_INVALID_LYRICSTRACK";
              }
            }
            else if (in_stack_00000004 < -0x3ff6fffe) {
              if (in_stack_00000004 == -0x3ff6ffff) {
                return (int)"ERROR_AUDITING_DISABLED";
              }
              switch(in_stack_00000004) {
              case -0x7787eddd:
                return (int)"DMUS_E_AUDIOVBSCRIPT_SYNTAXERROR";
              case -0x7787eddc:
                return (int)"DMUS_E_AUDIOVBSCRIPT_RUNTIMEERROR";
              case -0x7787eddb:
                return (int)"DMUS_E_AUDIOVBSCRIPT_OPERATIONFAILURE";
              case -0x7787edda:
                return (int)"DMUS_E_AUDIOPATHS_NOT_VALID";
              case -0x7787edd9:
                return (int)"DMUS_E_AUDIOPATHS_IN_USE";
              case -0x7787edd8:
                return (int)"DMUS_E_NO_AUDIOPATH_CONFIG";
              case -0x7787edd7:
                return (int)"DMUS_E_AUDIOPATH_INACTIVE";
              case -0x7787edd6:
                return (int)"DMUS_E_AUDIOPATH_NOBUFFER";
              case -0x7787edd5:
                return (int)"DMUS_E_AUDIOPATH_NOPORT";
              case -0x7787edd4:
                return (int)"DMUS_E_NO_AUDIOPATH";
              case -0x7787edd3:
                return (int)"DMUS_E_INVALIDCHUNK";
              case -0x7787edd2:
                return (int)"DMUS_E_AUDIOPATH_NOGLOBALFXBUFFER";
              case -0x7787edd1:
                return (int)"DMUS_E_INVALID_CONTAINER_OBJECT";
              }
            }
            else {
              if (in_stack_00000004 == -0x3ff6fffe) {
                return (int)"ERROR_ALL_SIDS_FILTERED";
              }
              if (in_stack_00000004 == 0) {
                return (int)&DAT_00602548;
              }
              if (in_stack_00000004 == 1) {
                return (int)"S_FALSE";
              }
              if (in_stack_00000004 == 2) {
LAB_005c042a:
                return (int)"ERROR_FILE_NOT_FOUND";
              }
              if (in_stack_00000004 == 3) goto LAB_005c46a0;
              if (in_stack_00000004 == 4) goto switchD_005c0442_caseD_80070004;
            }
          }
          else {
            switch(in_stack_00000004) {
            case 6:
              return (int)"ERROR_INVALID_HANDLE";
            case 7:
switchD_005c0442_caseD_80070007:
              return (int)"ERROR_ARENA_TRASHED";
            case 8:
switchD_005c0442_caseD_80070008:
              return (int)"ERROR_NOT_ENOUGH_MEMORY";
            case 9:
switchD_005c0442_caseD_80070009:
              return (int)"ERROR_INVALID_BLOCK";
            case 10:
switchD_005c0442_caseD_8007000a:
              return (int)"ERROR_BAD_ENVIRONMENT";
            case 0xb:
switchD_005c0442_caseD_8007000b:
              return (int)"ERROR_BAD_FORMAT";
            case 0xc:
switchD_005c0442_caseD_8007000c:
              return (int)"ERROR_INVALID_ACCESS & DIERR_NOTACQUIRED";
            case 0xd:
switchD_005c0442_caseD_8007000d:
              return (int)"ERROR_INVALID_DATA";
            case 0xe:
              return (int)"ERROR_OUTOFMEMORY";
            case 0xf:
switchD_005c0442_caseD_8007000f:
              return (int)"ERROR_INVALID_DRIVE";
            case 0x10:
switchD_005c0442_caseD_80070010:
              return (int)"ERROR_CURRENT_DIRECTORY";
            case 0x11:
switchD_005c0442_caseD_80070011:
              return (int)"ERROR_NOT_SAME_DEVICE";
            case 0x12:
switchD_005c0442_caseD_80070012:
              return (int)"ERROR_NO_MORE_FILES";
            case 0x13:
switchD_005c0442_caseD_80070013:
              return (int)"ERROR_WRITE_PROTECT";
            case 0x14:
switchD_005c0442_caseD_80070014:
              return (int)"ERROR_BAD_UNIT";
            case 0x15:
switchD_005c0442_caseD_80070015:
              return (int)"ERROR_NOT_READY & DIERR_NOTINITIALIZED";
            case 0x16:
switchD_005c0442_caseD_80070016:
              return (int)"ERROR_BAD_COMMAND";
            case 0x17:
switchD_005c0442_caseD_80070017:
              return (int)"ERROR_CRC";
            case 0x18:
switchD_005c0442_caseD_80070018:
              return (int)"ERROR_BAD_LENGTH";
            case 0x19:
switchD_005c0442_caseD_80070019:
              return (int)"ERROR_SEEK";
            case 0x1a:
switchD_005c0442_caseD_8007001a:
              return (int)"ERROR_NOT_DOS_DISK";
            case 0x1b:
switchD_005c0442_caseD_8007001b:
              return (int)"ERROR_SECTOR_NOT_FOUND";
            case 0x1c:
switchD_005c0442_caseD_8007001c:
              return (int)"ERROR_OUT_OF_PAPER";
            case 0x1d:
switchD_005c0442_caseD_8007001d:
              return (int)"ERROR_WRITE_FAULT";
            case 0x1e:
switchD_005c0442_caseD_8007001e:
              return (int)"ERROR_READ_FAULT & DIERR_INPUTLOST";
            case 0x1f:
switchD_005c0442_caseD_8007001f:
              return (int)"ERROR_GEN_FAILURE";
            case 0x20:
switchD_005c0442_caseD_80070020:
              return (int)"ERROR_SHARING_VIOLATION";
            case 0x21:
switchD_005c0442_caseD_80070021:
              return (int)"ERROR_LOCK_VIOLATION";
            case 0x22:
switchD_005c0442_caseD_80070022:
              return (int)"ERROR_WRONG_DISK";
            case 0x24:
switchD_005c46de_caseD_24:
              return (int)"ERROR_SHARING_BUFFER_EXCEEDED";
            case 0x26:
switchD_005c047c_caseD_80070026:
              return (int)"ERROR_HANDLE_EOF";
            case 0x27:
switchD_005c047c_caseD_80070027:
              return (int)"ERROR_HANDLE_DISK_FULL";
            case 0x32:
switchD_005c047c_caseD_80070032:
              return (int)"ERROR_NOT_SUPPORTED";
            case 0x33:
switchD_005c047c_caseD_80070033:
              return (int)"ERROR_REM_NOT_LIST";
            case 0x34:
switchD_005c047c_caseD_80070034:
              return (int)"ERROR_DUP_NAME";
            case 0x35:
switchD_005c047c_caseD_80070035:
              return (int)"ERROR_BAD_NETPATH";
            case 0x36:
switchD_005c047c_caseD_80070036:
              return (int)"ERROR_NETWORK_BUSY";
            case 0x37:
switchD_005c047c_caseD_80070037:
              return (int)"ERROR_DEV_NOT_EXIST";
            case 0x38:
switchD_005c047c_caseD_80070038:
              return (int)"ERROR_TOO_MANY_CMDS";
            case 0x39:
switchD_005c047c_caseD_80070039:
              return (int)"ERROR_ADAP_HDW_ERR";
            case 0x3a:
switchD_005c047c_caseD_8007003a:
              return (int)"ERROR_BAD_NET_RESP";
            }
          }
        }
        else {
          switch(in_stack_00000004) {
          case 0x3c:
switchD_005c047c_caseD_8007003c:
            return (int)"ERROR_BAD_REM_ADAP";
          case 0x3d:
switchD_005c047c_caseD_8007003d:
            return (int)"ERROR_PRINTQ_FULL";
          case 0x3e:
switchD_005c047c_caseD_8007003e:
            return (int)"ERROR_NO_SPOOL_SPACE";
          case 0x3f:
switchD_005c047c_caseD_8007003f:
            return (int)"ERROR_PRINT_CANCELLED";
          case 0x40:
switchD_005c047c_caseD_80070040:
            return (int)"ERROR_NETNAME_DELETED";
          case 0x41:
switchD_005c047c_caseD_80070041:
            return (int)"ERROR_NETWORK_ACCESS_DENIED";
          case 0x42:
switchD_005c047c_caseD_80070042:
            return (int)"ERROR_BAD_DEV_TYPE";
          case 0x43:
switchD_005c047c_caseD_80070043:
            return (int)"ERROR_BAD_NET_NAME";
          case 0x44:
switchD_005c047c_caseD_80070044:
            return (int)"ERROR_TOO_MANY_NAMES";
          case 0x45:
switchD_005c047c_caseD_80070045:
            return (int)"ERROR_TOO_MANY_SESS";
          case 0x46:
switchD_005c047c_caseD_80070046:
            return (int)"ERROR_SHARING_PAUSED";
          case 0x47:
switchD_005c047c_caseD_80070047:
            return (int)"ERROR_REQ_NOT_ACCEP";
          case 0x48:
switchD_005c047c_caseD_80070048:
            return (int)"ERROR_REDIR_PAUSED";
          case 0x50:
switchD_005c047c_caseD_80070050:
            return (int)"ERROR_FILE_EXISTS";
          case 0x52:
switchD_005c047c_caseD_80070052:
            return (int)"ERROR_CANNOT_MAKE";
          case 0x53:
switchD_005c047c_caseD_80070053:
            return (int)"ERROR_FAIL_I24";
          case 0x54:
switchD_005c047c_caseD_80070054:
            return (int)"ERROR_OUT_OF_STRUCTURES";
          case 0x55:
switchD_005c047c_caseD_80070055:
            return (int)"ERROR_ALREADY_ASSIGNED";
          case 0x56:
switchD_005c047c_caseD_80070056:
            return (int)"ERROR_INVALID_PASSWORD";
          case 0x57:
            return (int)"ERROR_INVALID_PARAMETER";
          case 0x58:
switchD_005c047c_caseD_80070058:
            return (int)"ERROR_NET_WRITE_FAULT";
          case 0x59:
switchD_005c047c_caseD_80070059:
            return (int)"ERROR_NO_PROC_SLOTS";
          case 100:
switchD_005c047c_caseD_80070064:
            return (int)"ERROR_TOO_MANY_SEMAPHORES";
          case 0x65:
switchD_005c047c_caseD_80070065:
            return (int)"ERROR_EXCL_SEM_ALREADY_OWNED";
          case 0x66:
switchD_005c047c_caseD_80070066:
            return (int)"ERROR_SEM_IS_SET";
          case 0x67:
switchD_005c047c_caseD_80070067:
            return (int)"ERROR_TOO_MANY_SEM_REQUESTS";
          case 0x68:
switchD_005c047c_caseD_80070068:
            return (int)"ERROR_INVALID_AT_INTERRUPT_TIME";
          case 0x69:
switchD_005c047c_caseD_80070069:
            return (int)"ERROR_SEM_OWNER_DIED";
          case 0x6a:
switchD_005c047c_caseD_8007006a:
            return (int)"ERROR_SEM_USER_LIMIT";
          case 0x6b:
switchD_005c047c_caseD_8007006b:
            return (int)"ERROR_DISK_CHANGE";
          case 0x6c:
switchD_005c047c_caseD_8007006c:
            return (int)"ERROR_DRIVE_LOCKED";
          case 0x6d:
switchD_005c047c_caseD_8007006d:
            return (int)"ERROR_BROKEN_PIPE";
          case 0x6e:
switchD_005c047c_caseD_8007006e:
            return (int)"ERROR_OPEN_FAILED";
          case 0x6f:
switchD_005c047c_caseD_8007006f:
            return (int)"ERROR_BUFFER_OVERFLOW";
          case 0x70:
switchD_005c047c_caseD_80070070:
            return (int)"ERROR_DISK_FULL";
          case 0x71:
switchD_005c047c_caseD_80070071:
            return (int)"ERROR_NO_MORE_SEARCH_HANDLES";
          case 0x72:
switchD_005c047c_caseD_80070072:
            return (int)"ERROR_INVALID_TARGET_HANDLE";
          case 0x75:
switchD_005c047c_caseD_80070075:
            return (int)"ERROR_INVALID_CATEGORY";
          case 0x76:
switchD_005c047c_caseD_80070076:
            return (int)"ERROR_INVALID_VERIFY_SWITCH";
          case 0x77:
switchD_005c047c_caseD_80070077:
            return (int)"ERROR_BAD_DRIVER_LEVEL & DIERR_BADDRIVERVER";
          case 0x78:
switchD_005c047c_caseD_80070078:
            return (int)"ERROR_CALL_NOT_IMPLEMENTED";
          case 0x79:
switchD_005c047c_caseD_80070079:
            return (int)"ERROR_SEM_TIMEOUT";
          case 0x7a:
switchD_005c047c_caseD_8007007a:
            return (int)"ERROR_INSUFFICIENT_BUFFER";
          case 0x7b:
switchD_005c047c_caseD_8007007b:
            return (int)"ERROR_INVALID_NAME";
          case 0x7c:
switchD_005c047c_caseD_8007007c:
            return (int)"ERROR_INVALID_LEVEL";
          case 0x7d:
switchD_005c047c_caseD_8007007d:
            return (int)"ERROR_NO_VOLUME_LABEL";
          case 0x7e:
switchD_005c047c_caseD_8007007e:
            return (int)"ERROR_MOD_NOT_FOUND";
          case 0x7f:
switchD_005c047c_caseD_8007007f:
            return (int)"ERROR_PROC_NOT_FOUND";
          case 0x80:
switchD_005c047c_caseD_80070080:
            return (int)"ERROR_WAIT_NO_CHILDREN";
          case 0x81:
switchD_005c047c_caseD_80070081:
            return (int)"ERROR_CHILD_NOT_COMPLETE";
          case 0x82:
            goto switchD_005c4895_caseD_82;
          case 0x83:
            goto switchD_005c04b1_caseD_80070083;
          case 0x84:
            goto switchD_005c04b1_caseD_80070084;
          case 0x85:
            goto switchD_005c04b1_caseD_80070085;
          case 0x86:
            goto switchD_005c04b1_caseD_80070086;
          case 0x87:
            goto switchD_005c04b1_caseD_80070087;
          case 0x88:
            goto switchD_005c04b1_caseD_80070088;
          case 0x89:
            goto switchD_005c04b1_caseD_80070089;
          case 0x8a:
            goto switchD_005c04b1_caseD_8007008a;
          case 0x8b:
            goto switchD_005c04b1_caseD_8007008b;
          case 0x8c:
            goto switchD_005c04b1_caseD_8007008c;
          case 0x8d:
            goto switchD_005c04b1_caseD_8007008d;
          case 0x8e:
            goto switchD_005c04b1_caseD_8007008e;
          case 0x8f:
            goto switchD_005c04b1_caseD_8007008f;
          case 0x90:
            goto switchD_005c04b1_caseD_80070090;
          case 0x91:
            goto switchD_005c04b1_caseD_80070091;
          case 0x92:
            goto switchD_005c04b1_caseD_80070092;
          case 0x93:
            goto switchD_005c04b1_caseD_80070093;
          case 0x94:
            goto switchD_005c04b1_caseD_80070094;
          case 0x95:
            goto switchD_005c04b1_caseD_80070095;
          case 0x96:
            goto switchD_005c04b1_caseD_80070096;
          case 0x97:
            goto switchD_005c04b1_caseD_80070097;
          case 0x98:
            goto switchD_005c04b1_caseD_80070098;
          case 0x99:
            goto switchD_005c04b1_caseD_80070099;
          case 0x9a:
            goto switchD_005c04b1_caseD_8007009a;
          case 0x9b:
            goto switchD_005c04b1_caseD_8007009b;
          case 0x9c:
            goto switchD_005c04b1_caseD_8007009c;
          case 0x9d:
            goto switchD_005c04b1_caseD_8007009d;
          case 0x9e:
            goto switchD_005c04b1_caseD_8007009e;
          case 0x9f:
            goto switchD_005c04b1_caseD_8007009f;
          case 0xa0:
            goto switchD_005c04b1_caseD_800700a0;
          case 0xa1:
            goto switchD_005c04b1_caseD_800700a1;
          }
        }
      }
      else if (in_stack_00000004 < 0x3f2) {
        if (in_stack_00000004 == 0x3f1) {
switchD_005c05d1_caseD_800703f1:
          return (int)"ERROR_BADDB";
        }
        if (in_stack_00000004 < 0xea) {
          if (in_stack_00000004 == 0xe9) goto switchD_005c04b1_caseD_800700e9;
          switch(in_stack_00000004) {
          case 0xa4:
            goto switchD_005c04b1_caseD_800700a4;
          case 0xa7:
            goto switchD_005c04b1_caseD_800700a7;
          case 0xaa:
            goto switchD_005c04b1_caseD_800700aa;
          case 0xad:
            goto switchD_005c04b1_caseD_800700ad;
          case 0xae:
            goto switchD_005c04b1_caseD_800700ae;
          case 0xb4:
            goto switchD_005c04b1_caseD_800700b4;
          case 0xb6:
            goto switchD_005c04b1_caseD_800700b6;
          case 0xb7:
            goto switchD_005c04b1_caseD_800700b7;
          case 0xba:
            goto switchD_005c04b1_caseD_800700ba;
          case 0xbb:
            goto switchD_005c04b1_caseD_800700bb;
          case 0xbc:
            goto switchD_005c04b1_caseD_800700bc;
          case 0xbd:
            goto switchD_005c04b1_caseD_800700bd;
          case 0xbe:
            goto switchD_005c04b1_caseD_800700be;
          case 0xbf:
            goto switchD_005c04b1_caseD_800700bf;
          case 0xc0:
            goto switchD_005c04b1_caseD_800700c0;
          case 0xc1:
            goto switchD_005c04b1_caseD_800700c1;
          case 0xc2:
            goto switchD_005c04b1_caseD_800700c2;
          case 0xc3:
            goto switchD_005c04b1_caseD_800700c3;
          case 0xc4:
            goto switchD_005c04b1_caseD_800700c4;
          case 0xc5:
            goto switchD_005c04b1_caseD_800700c5;
          case 0xc6:
            goto switchD_005c04b1_caseD_800700c6;
          case 199:
            goto switchD_005c04b1_caseD_800700c7;
          case 200:
            return (int)"ERROR_RING2SEG_MUST_BE_MOVABLE";
          case 0xc9:
            return (int)"ERROR_RELOC_CHAIN_XEEDS_SEGLIM";
          case 0xca:
            goto switchD_005c04b1_caseD_800700ca;
          case 0xcb:
            goto switchD_005c04b1_caseD_800700cb;
          case 0xcd:
            goto switchD_005c04b1_caseD_800700cd;
          case 0xce:
            goto switchD_005c04b1_caseD_800700ce;
          case 0xcf:
            goto switchD_005c04b1_caseD_800700cf;
          case 0xd0:
            goto switchD_005c04b1_caseD_800700d0;
          case 0xd1:
            goto switchD_005c04b1_caseD_800700d1;
          case 0xd2:
            goto switchD_005c04b1_caseD_800700d2;
          case 0xd4:
            goto switchD_005c04b1_caseD_800700d4;
          case 0xd6:
            goto switchD_005c04b1_caseD_800700d6;
          case 0xd7:
            goto switchD_005c04b1_caseD_800700d7;
          case 0xd8:
            goto switchD_005c04b1_caseD_800700d8;
          case 0xd9:
            goto switchD_005c04b1_caseD_800700d9;
          case 0xda:
            goto switchD_005c04b1_caseD_800700da;
          case 0xe6:
            goto switchD_005c04b1_caseD_800700e6;
          case 0xe7:
            goto switchD_005c04b1_caseD_800700e7;
          case 0xe8:
            goto switchD_005c04b1_caseD_800700e8;
          }
        }
        else if (in_stack_00000004 < 0x13e) {
          if (in_stack_00000004 == 0x13d) {
LAB_005c4eb7:
            return (int)"ERROR_MR_MID_NOT_FOUND";
          }
          switch(in_stack_00000004) {
          case 0xea:
            goto switchD_005c04b1_caseD_800700ea;
          case 0xf0:
            goto switchD_005c4de8_caseD_f0;
          case 0xfe:
switchD_005c0526_caseD_800700fe:
            return (int)"ERROR_INVALID_EA_NAME";
          case 0xff:
switchD_005c0526_caseD_800700ff:
            return (int)"ERROR_EA_LIST_INCONSISTENT";
          case 0x102:
switchD_005c0526_caseD_80070102:
            return (int)"WAIT_TIMEOUT";
          case 0x103:
switchD_005c0526_caseD_80070103:
            return (int)"ERROR_NO_MORE_ITEMS & DIERR_NOMOREITEMS";
          case 0x10a:
switchD_005c0526_caseD_8007010a:
            return (int)"ERROR_CANNOT_COPY";
          case 0x10b:
switchD_005c0526_caseD_8007010b:
            return (int)"ERROR_DIRECTORY";
          case 0x113:
switchD_005c0526_caseD_80070113:
            return (int)"ERROR_EAS_DIDNT_FIT";
          case 0x114:
switchD_005c0526_caseD_80070114:
            return (int)"ERROR_EA_FILE_CORRUPT";
          case 0x115:
switchD_005c0526_caseD_80070115:
            return (int)"ERROR_EA_TABLE_FULL";
          case 0x116:
switchD_005c0526_caseD_80070116:
            return (int)"ERROR_INVALID_EA_HANDLE";
          case 0x11a:
switchD_005c0526_caseD_8007011a:
            return (int)"ERROR_EAS_NOT_SUPPORTED";
          case 0x120:
switchD_005c0526_caseD_80070120:
            return (int)"ERROR_NOT_OWNER";
          case 0x12a:
switchD_005c0526_caseD_8007012a:
            return (int)"ERROR_TOO_MANY_POSTS";
          case 299:
switchD_005c0526_caseD_8007012b:
            return (int)"ERROR_PARTIAL_COPY";
          case 300:
switchD_005c0526_caseD_8007012c:
            return (int)"ERROR_OPLOCK_NOT_GRANTED";
          case 0x12d:
switchD_005c0526_caseD_8007012d:
            return (int)"ERROR_INVALID_OPLOCK_PROTOCOL";
          case 0x12e:
switchD_005c0526_caseD_8007012e:
            return (int)"ERROR_DISK_TOO_FRAGMENTED";
          case 0x12f:
switchD_005c0526_caseD_8007012f:
            return (int)"ERROR_DELETE_PENDING";
          }
        }
        else if (in_stack_00000004 < 999) {
          if (in_stack_00000004 == 0x3e6) {
switchD_005c05b5_caseD_800703e6:
            return (int)"ERROR_NOACCESS";
          }
          if (in_stack_00000004 < 0x219) {
            if (in_stack_00000004 == 0x218) {
LAB_005c4f21:
              return (int)"ERROR_PIPE_LISTENING";
            }
            if (in_stack_00000004 == 0x13e) {
LAB_005c4f17:
              return (int)"ERROR_SCOPE_NOT_FOUND";
            }
            if (in_stack_00000004 == 0x1e7) {
LAB_005c4f0d:
              return (int)"ERROR_INVALID_ADDRESS";
            }
            if (in_stack_00000004 == 0x216) {
LAB_005c4f03:
              return (int)"ERROR_ARITHMETIC_OVERFLOW";
            }
            if (in_stack_00000004 == 0x217) {
LAB_005c4ef9:
              return (int)"ERROR_PIPE_CONNECTED";
            }
          }
          else {
            if (in_stack_00000004 == 0x3e2) {
LAB_005c4f57:
              return (int)"ERROR_EA_ACCESS_DENIED";
            }
            if (in_stack_00000004 == 0x3e3) {
LAB_005c4f4d:
              return (int)"ERROR_OPERATION_ABORTED";
            }
            if (in_stack_00000004 == 0x3e4) {
LAB_005c059d:
              return (int)"ERROR_IO_INCOMPLETE";
            }
            if (in_stack_00000004 == 0x3e5) goto LAB_005c4f43;
          }
        }
        else {
          switch(in_stack_00000004) {
          case 999:
switchD_005c05b5_caseD_800703e7:
            return (int)"ERROR_SWAPERROR";
          case 0x3e9:
switchD_005c05b5_caseD_800703e9:
            return (int)"ERROR_STACK_OVERFLOW";
          case 0x3ea:
switchD_005c05b5_caseD_800703ea:
            return (int)"ERROR_INVALID_MESSAGE";
          case 0x3eb:
switchD_005c05b5_caseD_800703eb:
            return (int)"ERROR_CAN_NOT_COMPLETE";
          case 0x3ec:
switchD_005c05b5_caseD_800703ec:
            return (int)"ERROR_INVALID_FLAGS";
          case 0x3ed:
switchD_005c05b5_caseD_800703ed:
            return (int)"ERROR_UNRECOGNIZED_VOLUME";
          case 0x3ee:
switchD_005c05b5_caseD_800703ee:
            return (int)"ERROR_FILE_INVALID";
          case 0x3ef:
switchD_005c4f79_caseD_3ef:
            return (int)"ERROR_FULLSCREEN_MODE";
          case 0x3f0:
switchD_005c05d1_caseD_800703f0:
            return (int)"ERROR_NO_TOKEN";
          }
        }
      }
      else {
        switch(in_stack_00000004) {
        case 0x3f2:
switchD_005c05d1_caseD_800703f2:
          return (int)"ERROR_BADKEY";
        case 0x3f3:
switchD_005c05d1_caseD_800703f3:
          return (int)"ERROR_CANTOPEN";
        case 0x3f4:
switchD_005c05d1_caseD_800703f4:
          return (int)"ERROR_CANTREAD";
        case 0x3f5:
switchD_005c05d1_caseD_800703f5:
          return (int)"ERROR_CANTWRITE";
        case 0x3f6:
switchD_005c05d1_caseD_800703f6:
          return (int)"ERROR_REGISTRY_RECOVERED";
        case 0x3f7:
switchD_005c05d1_caseD_800703f7:
          return (int)"ERROR_REGISTRY_CORRUPT";
        case 0x3f8:
switchD_005c05d1_caseD_800703f8:
          return (int)"ERROR_REGISTRY_IO_FAILED";
        case 0x3f9:
switchD_005c05d1_caseD_800703f9:
          return (int)"ERROR_NOT_REGISTRY_FILE";
        case 0x3fa:
switchD_005c05d1_caseD_800703fa:
          return (int)"ERROR_KEY_DELETED";
        case 0x3fb:
switchD_005c05d1_caseD_800703fb:
          return (int)"ERROR_NO_LOG_SPACE";
        case 0x3fc:
switchD_005c05d1_caseD_800703fc:
          return (int)"ERROR_KEY_HAS_CHILDREN";
        case 0x3fd:
switchD_005c05d1_caseD_800703fd:
          return (int)"ERROR_CHILD_MUST_BE_VOLATILE";
        case 0x3fe:
switchD_005c05d1_caseD_800703fe:
          return (int)"ERROR_NOTIFY_ENUM_DIR";
        case 0x41b:
switchD_005c05d1_caseD_8007041b:
          return (int)"ERROR_DEPENDENT_SERVICES_RUNNING";
        case 0x41c:
switchD_005c05d1_caseD_8007041c:
          return (int)"ERROR_INVALID_SERVICE_CONTROL";
        case 0x41d:
switchD_005c05d1_caseD_8007041d:
          return (int)"ERROR_SERVICE_REQUEST_TIMEOUT";
        case 0x41e:
switchD_005c05d1_caseD_8007041e:
          return (int)"ERROR_SERVICE_NO_THREAD";
        case 0x41f:
switchD_005c05d1_caseD_8007041f:
          return (int)"ERROR_SERVICE_DATABASE_LOCKED";
        case 0x420:
switchD_005c05d1_caseD_80070420:
          return (int)"ERROR_SERVICE_ALREADY_RUNNING";
        case 0x421:
switchD_005c05d1_caseD_80070421:
          return (int)"ERROR_INVALID_SERVICE_ACCOUNT";
        case 0x422:
switchD_005c05d1_caseD_80070422:
          return (int)"ERROR_SERVICE_DISABLED";
        case 0x423:
switchD_005c05d1_caseD_80070423:
          return (int)"ERROR_CIRCULAR_DEPENDENCY";
        case 0x424:
switchD_005c05d1_caseD_80070424:
          return (int)"ERROR_SERVICE_DOES_NOT_EXIST";
        case 0x425:
switchD_005c05d1_caseD_80070425:
          return (int)"ERROR_SERVICE_CANNOT_ACCEPT_CTRL";
        case 0x426:
switchD_005c05d1_caseD_80070426:
          return (int)"ERROR_SERVICE_NOT_ACTIVE";
        case 0x427:
switchD_005c05d1_caseD_80070427:
          return (int)"ERROR_FAILED_SERVICE_CONTROLLER_CONNECT";
        case 0x428:
switchD_005c05d1_caseD_80070428:
          return (int)"ERROR_EXCEPTION_IN_SERVICE";
        case 0x429:
switchD_005c05d1_caseD_80070429:
          return (int)"ERROR_DATABASE_DOES_NOT_EXIST";
        case 0x42a:
switchD_005c05d1_caseD_8007042a:
          return (int)"ERROR_SERVICE_SPECIFIC_ERROR";
        case 0x42b:
switchD_005c05d1_caseD_8007042b:
          return (int)"ERROR_PROCESS_ABORTED";
        case 0x42c:
switchD_005c05d1_caseD_8007042c:
          return (int)"ERROR_SERVICE_DEPENDENCY_FAIL";
        case 0x42d:
switchD_005c05d1_caseD_8007042d:
          return (int)"ERROR_SERVICE_LOGON_FAILED";
        case 0x42e:
switchD_005c05d1_caseD_8007042e:
          return (int)"ERROR_SERVICE_START_HANG";
        case 0x42f:
switchD_005c05d1_caseD_8007042f:
          return (int)"ERROR_INVALID_SERVICE_LOCK";
        case 0x430:
switchD_005c4ffb_caseD_430:
          return (int)"ERROR_SERVICE_MARKED_FOR_DELETE";
        case 0x431:
switchD_005c05ed_caseD_80070431:
          return (int)"ERROR_SERVICE_EXISTS";
        case 0x432:
switchD_005c05ed_caseD_80070432:
          return (int)"ERROR_ALREADY_RUNNING_LKG";
        case 0x433:
switchD_005c05ed_caseD_80070433:
          return (int)"ERROR_SERVICE_DEPENDENCY_DELETED";
        case 0x434:
switchD_005c05ed_caseD_80070434:
          return (int)"ERROR_BOOT_ALREADY_ACCEPTED";
        case 0x435:
switchD_005c05ed_caseD_80070435:
          return (int)"ERROR_SERVICE_NEVER_STARTED";
        case 0x436:
switchD_005c05ed_caseD_80070436:
          return (int)"ERROR_DUPLICATE_SERVICE_NAME";
        case 0x437:
switchD_005c05ed_caseD_80070437:
          return (int)"ERROR_DIFFERENT_SERVICE_ACCOUNT";
        case 0x438:
switchD_005c05ed_caseD_80070438:
          return (int)"ERROR_CANNOT_DETECT_DRIVER_FAILURE";
        case 0x439:
switchD_005c05ed_caseD_80070439:
          return (int)"ERROR_CANNOT_DETECT_PROCESS_ABORT";
        case 0x43a:
switchD_005c05ed_caseD_8007043a:
          return (int)"ERROR_NO_RECOVERY_PROGRAM";
        case 0x43b:
switchD_005c05ed_caseD_8007043b:
          return (int)"ERROR_SERVICE_NOT_IN_EXE";
        case 0x43c:
switchD_005c05ed_caseD_8007043c:
          return (int)"ERROR_NOT_SAFEBOOT_SERVICE";
        case 0x44c:
switchD_005c05ed_caseD_8007044c:
          return (int)"ERROR_END_OF_MEDIA";
        case 0x44d:
switchD_005c05ed_caseD_8007044d:
          return (int)"ERROR_FILEMARK_DETECTED";
        case 0x44e:
switchD_005c05ed_caseD_8007044e:
          return (int)"ERROR_BEGINNING_OF_MEDIA";
        case 0x44f:
switchD_005c05ed_caseD_8007044f:
          return (int)"ERROR_SETMARK_DETECTED";
        case 0x450:
switchD_005c05ed_caseD_80070450:
          return (int)"ERROR_NO_DATA_DETECTED";
        case 0x451:
switchD_005c05ed_caseD_80070451:
          return (int)"ERROR_PARTITION_FAILURE";
        case 0x452:
switchD_005c05ed_caseD_80070452:
          return (int)"ERROR_INVALID_BLOCK_LENGTH";
        case 0x453:
switchD_005c05ed_caseD_80070453:
          return (int)"ERROR_DEVICE_NOT_PARTITIONED";
        case 0x454:
switchD_005c05ed_caseD_80070454:
          return (int)"ERROR_UNABLE_TO_LOCK_MEDIA";
        case 0x455:
switchD_005c05ed_caseD_80070455:
          return (int)"ERROR_UNABLE_TO_UNLOAD_MEDIA";
        case 0x456:
switchD_005c05ed_caseD_80070456:
          return (int)"ERROR_MEDIA_CHANGED";
        case 0x457:
switchD_005c05ed_caseD_80070457:
          return (int)"ERROR_BUS_RESET";
        case 0x458:
switchD_005c05ed_caseD_80070458:
          return (int)"ERROR_NO_MEDIA_IN_DRIVE";
        case 0x459:
switchD_005c05ed_caseD_80070459:
          return (int)"ERROR_NO_UNICODE_TRANSLATION";
        case 0x45a:
switchD_005c05ed_caseD_8007045a:
          return (int)"ERROR_DLL_INIT_FAILED";
        case 0x45b:
switchD_005c05ed_caseD_8007045b:
          return (int)"ERROR_SHUTDOWN_IN_PROGRESS";
        case 0x45c:
switchD_005c05ed_caseD_8007045c:
          return (int)"ERROR_NO_SHUTDOWN_IN_PROGRESS";
        case 0x45d:
switchD_005c05ed_caseD_8007045d:
          return (int)"ERROR_IO_DEVICE";
        case 0x45e:
switchD_005c05ed_caseD_8007045e:
          return (int)"ERROR_SERIAL_NO_DEVICE";
        case 0x45f:
switchD_005c05ed_caseD_8007045f:
          return (int)"ERROR_IRQ_BUSY";
        case 0x460:
switchD_005c05ed_caseD_80070460:
          return (int)"ERROR_MORE_WRITES";
        case 0x461:
switchD_005c05ed_caseD_80070461:
          return (int)"ERROR_COUNTER_TIMEOUT";
        case 0x462:
switchD_005c05ed_caseD_80070462:
          return (int)"ERROR_FLOPPY_ID_MARK_NOT_FOUND";
        case 0x463:
switchD_005c05ed_caseD_80070463:
          return (int)"ERROR_FLOPPY_WRONG_CYLINDER";
        case 0x464:
switchD_005c05ed_caseD_80070464:
          return (int)"ERROR_FLOPPY_UNKNOWN_ERROR";
        case 0x465:
switchD_005c05ed_caseD_80070465:
          return (int)"ERROR_FLOPPY_BAD_REGISTERS";
        case 0x466:
switchD_005c05ed_caseD_80070466:
          return (int)"ERROR_DISK_RECALIBRATE_FAILED";
        case 0x467:
switchD_005c05ed_caseD_80070467:
          return (int)"ERROR_DISK_OPERATION_FAILED";
        case 0x468:
switchD_005c05ed_caseD_80070468:
          return (int)"ERROR_DISK_RESET_FAILED";
        case 0x469:
switchD_005c05ed_caseD_80070469:
          return (int)"ERROR_EOM_OVERFLOW";
        case 0x46a:
switchD_005c05ed_caseD_8007046a:
          return (int)"ERROR_NOT_ENOUGH_SERVER_MEMORY";
        case 0x46b:
switchD_005c05ed_caseD_8007046b:
          return (int)"ERROR_POSSIBLE_DEADLOCK";
        case 0x46c:
switchD_005c05ed_caseD_8007046c:
          return (int)"ERROR_MAPPED_ALIGNMENT";
        case 0x474:
switchD_005c05ed_caseD_80070474:
          return (int)"ERROR_SET_POWER_STATE_VETOED";
        case 0x475:
switchD_005c05ed_caseD_80070475:
          return (int)"ERROR_SET_POWER_STATE_FAILED";
        }
      }
    }
    else {
      switch(in_stack_00000004) {
      case 0x47e:
switchD_005c05ed_caseD_8007047e:
        return (int)"ERROR_OLD_WIN_VERSION & DIERR_OLDDIRECTINPUTVERSION";
      case 0x47f:
switchD_005c05ed_caseD_8007047f:
        return (int)"ERROR_APP_WRONG_OS";
      case 0x480:
switchD_005c05ed_caseD_80070480:
        return (int)"ERROR_SINGLE_INSTANCE_APP";
      case 0x481:
switchD_005c05ed_caseD_80070481:
        return (int)"ERROR_RMODE_APP & DIERR_BETADIRECTINPUTVERSION";
      case 0x482:
switchD_005c05ed_caseD_80070482:
        return (int)"ERROR_INVALID_DLL";
      case 0x483:
switchD_005c05ed_caseD_80070483:
        return (int)"ERROR_NO_ASSOCIATION";
      case 0x484:
switchD_005c05ed_caseD_80070484:
        return (int)"ERROR_DDE_FAIL";
      case 0x485:
switchD_005c05ed_caseD_80070485:
        return (int)"ERROR_DLL_NOT_FOUND";
      case 0x486:
switchD_005c05ed_caseD_80070486:
        return (int)"ERROR_NO_MORE_USER_HANDLES";
      case 0x487:
switchD_005c05ed_caseD_80070487:
        return (int)"ERROR_MESSAGE_SYNC_ONLY";
      case 0x488:
switchD_005c05ed_caseD_80070488:
        return (int)"ERROR_SOURCE_ELEMENT_EMPTY";
      case 0x489:
switchD_005c05ed_caseD_80070489:
        return (int)"ERROR_DESTINATION_ELEMENT_FULL";
      case 0x48a:
switchD_005c05ed_caseD_8007048a:
        return (int)"ERROR_ILLEGAL_ELEMENT_ADDRESS";
      case 0x48b:
switchD_005c05ed_caseD_8007048b:
        return (int)"ERROR_MAGAZINE_NOT_PRESENT";
      case 0x48c:
switchD_005c05ed_caseD_8007048c:
        return (int)"ERROR_DEVICE_REINITIALIZATION_NEEDED";
      case 0x48d:
switchD_005c05ed_caseD_8007048d:
        return (int)"ERROR_DEVICE_REQUIRES_CLEANING";
      case 0x48e:
switchD_005c05ed_caseD_8007048e:
        return (int)"ERROR_DEVICE_DOOR_OPEN";
      case 0x48f:
switchD_005c05ed_caseD_8007048f:
        return (int)"ERROR_DEVICE_NOT_CONNECTED";
      case 0x490:
switchD_005c05ed_caseD_80070490:
        return (int)"ERROR_NOT_FOUND & E_PROP_ID_UNSUPPORTED";
      case 0x491:
switchD_005c05ed_caseD_80070491:
        return (int)"ERROR_NO_MATCH";
      case 0x492:
switchD_005c05ed_caseD_80070492:
        return (int)"ERROR_SET_NOT_FOUND & E_PROP_SET_UNSUPPORTED";
      case 0x493:
switchD_005c05ed_caseD_80070493:
        return (int)"ERROR_POINT_NOT_FOUND";
      case 0x494:
switchD_005c05ed_caseD_80070494:
        return (int)"ERROR_NO_TRACKING_SERVICE";
      case 0x495:
switchD_005c05ed_caseD_80070495:
        return (int)"ERROR_NO_VOLUME_ID";
      case 0x497:
switchD_005c05ed_caseD_80070497:
        return (int)"ERROR_UNABLE_TO_REMOVE_REPLACED";
      case 0x498:
switchD_005c5350_caseD_498:
        return (int)"ERROR_UNABLE_TO_MOVE_REPLACEMENT";
      case 0x499:
switchD_005c0604_caseD_80070499:
        return (int)"ERROR_UNABLE_TO_MOVE_REPLACEMENT_2";
      case 0x49a:
switchD_005c0604_caseD_8007049a:
        return (int)"ERROR_JOURNAL_DELETE_IN_PROGRESS";
      case 0x49b:
switchD_005c0604_caseD_8007049b:
        return (int)"ERROR_JOURNAL_NOT_ACTIVE";
      case 0x49c:
switchD_005c0604_caseD_8007049c:
        return (int)"ERROR_POTENTIAL_FILE_FOUND";
      case 0x49d:
switchD_005c0604_caseD_8007049d:
        return (int)"ERROR_JOURNAL_ENTRY_DELETED";
      case 0x4b0:
switchD_005c0604_caseD_800704b0:
        return (int)"ERROR_BAD_DEVICE";
      case 0x4b1:
switchD_005c0604_caseD_800704b1:
        return (int)"ERROR_CONNECTION_UNAVAIL";
      case 0x4b2:
switchD_005c0604_caseD_800704b2:
        return (int)"ERROR_DEVICE_ALREADY_REMEMBERED";
      case 0x4b3:
switchD_005c0604_caseD_800704b3:
        return (int)"ERROR_NO_NET_OR_BAD_PATH";
      case 0x4b4:
switchD_005c0604_caseD_800704b4:
        return (int)"ERROR_BAD_PROVIDER";
      case 0x4b5:
switchD_005c0604_caseD_800704b5:
        return (int)"ERROR_CANNOT_OPEN_PROFILE";
      case 0x4b6:
switchD_005c0604_caseD_800704b6:
        return (int)"ERROR_BAD_PROFILE";
      case 0x4b7:
switchD_005c0604_caseD_800704b7:
        return (int)"ERROR_NOT_CONTAINER";
      case 0x4b8:
switchD_005c0604_caseD_800704b8:
        return (int)"ERROR_EXTENDED_ERROR";
      case 0x4b9:
switchD_005c0604_caseD_800704b9:
        return (int)"ERROR_INVALID_GROUPNAME";
      case 0x4ba:
switchD_005c0604_caseD_800704ba:
        return (int)"ERROR_INVALID_COMPUTERNAME";
      case 0x4bb:
switchD_005c0604_caseD_800704bb:
        return (int)"ERROR_INVALID_EVENTNAME";
      case 0x4bc:
switchD_005c0604_caseD_800704bc:
        return (int)"ERROR_INVALID_DOMAINNAME";
      case 0x4bd:
switchD_005c0604_caseD_800704bd:
        return (int)"ERROR_INVALID_SERVICENAME";
      case 0x4be:
switchD_005c0604_caseD_800704be:
        return (int)"ERROR_INVALID_NETNAME";
      case 0x4bf:
switchD_005c0604_caseD_800704bf:
        return (int)"ERROR_INVALID_SHARENAME";
      case 0x4c0:
switchD_005c0604_caseD_800704c0:
        return (int)"ERROR_INVALID_PASSWORDNAME";
      case 0x4c1:
switchD_005c0604_caseD_800704c1:
        return (int)"ERROR_INVALID_MESSAGENAME";
      case 0x4c2:
switchD_005c0604_caseD_800704c2:
        return (int)"ERROR_INVALID_MESSAGEDEST";
      case 0x4c3:
switchD_005c0604_caseD_800704c3:
        return (int)"ERROR_SESSION_CREDENTIAL_CONFLICT";
      case 0x4c4:
switchD_005c0604_caseD_800704c4:
        return (int)"ERROR_REMOTE_SESSION_LIMIT_EXCEEDED";
      case 0x4c5:
switchD_005c0604_caseD_800704c5:
        return (int)"ERROR_DUP_DOMAINNAME";
      case 0x4c6:
switchD_005c0604_caseD_800704c6:
        return (int)"ERROR_NO_NETWORK";
      case 0x4c7:
switchD_005c0604_caseD_800704c7:
        return (int)"ERROR_CANCELLED";
      case 0x4c8:
switchD_005c0604_caseD_800704c8:
        return (int)"ERROR_USER_MAPPED_FILE";
      case 0x4c9:
switchD_005c0604_caseD_800704c9:
        return (int)"ERROR_CONNECTION_REFUSED";
      case 0x4ca:
switchD_005c0604_caseD_800704ca:
        return (int)"ERROR_GRACEFUL_DISCONNECT";
      case 0x4cb:
switchD_005c0604_caseD_800704cb:
        return (int)"ERROR_ADDRESS_ALREADY_ASSOCIATED";
      case 0x4cc:
switchD_005c0604_caseD_800704cc:
        return (int)"ERROR_ADDRESS_NOT_ASSOCIATED";
      case 0x4cd:
switchD_005c0604_caseD_800704cd:
        return (int)"ERROR_CONNECTION_INVALID";
      case 0x4ce:
switchD_005c0604_caseD_800704ce:
        return (int)"ERROR_CONNECTION_ACTIVE";
      case 0x4cf:
switchD_005c0604_caseD_800704cf:
        return (int)"ERROR_NETWORK_UNREACHABLE";
      case 0x4d0:
switchD_005c0604_caseD_800704d0:
        return (int)"ERROR_HOST_UNREACHABLE";
      case 0x4d1:
switchD_005c0604_caseD_800704d1:
        return (int)"ERROR_PROTOCOL_UNREACHABLE";
      case 0x4d2:
switchD_005c0604_caseD_800704d2:
        return (int)"ERROR_PORT_UNREACHABLE";
      case 0x4d3:
switchD_005c0604_caseD_800704d3:
        return (int)"ERROR_REQUEST_ABORTED";
      case 0x4d4:
switchD_005c0604_caseD_800704d4:
        return (int)"ERROR_CONNECTION_ABORTED";
      case 0x4d5:
switchD_005c0604_caseD_800704d5:
        return (int)"ERROR_RETRY";
      case 0x4d6:
switchD_005c0604_caseD_800704d6:
        return (int)"ERROR_CONNECTION_COUNT_LIMIT";
      case 0x4d7:
switchD_005c0604_caseD_800704d7:
        return (int)"ERROR_LOGIN_TIME_RESTRICTION";
      case 0x4d8:
switchD_005c0604_caseD_800704d8:
        return (int)"ERROR_LOGIN_WKSTA_RESTRICTION";
      case 0x4d9:
switchD_005c0604_caseD_800704d9:
        return (int)"ERROR_INCORRECT_ADDRESS";
      case 0x4da:
switchD_005c0604_caseD_800704da:
        return (int)"ERROR_ALREADY_REGISTERED";
      case 0x4db:
switchD_005c0604_caseD_800704db:
        return (int)"ERROR_SERVICE_NOT_FOUND";
      case 0x4dc:
switchD_005c0604_caseD_800704dc:
        return (int)"ERROR_NOT_AUTHENTICATED";
      case 0x4dd:
switchD_005c0604_caseD_800704dd:
        return (int)"ERROR_NOT_LOGGED_ON";
      case 0x4de:
switchD_005c0604_caseD_800704de:
        return (int)"ERROR_CONTINUE";
      case 0x4df:
switchD_005c0604_caseD_800704df:
        return (int)"ERROR_ALREADY_INITIALIZED & DIERR_ALREADYINITIALIZED";
      case 0x4e0:
switchD_005c0604_caseD_800704e0:
        return (int)"ERROR_NO_MORE_DEVICES";
      case 0x4e1:
switchD_005c0604_caseD_800704e1:
        return (int)"ERROR_NO_SUCH_SITE";
      case 0x4e2:
switchD_005c0604_caseD_800704e2:
        return (int)"ERROR_DOMAIN_CONTROLLER_EXISTS";
      case 0x4e3:
switchD_005c0604_caseD_800704e3:
        return (int)"ERROR_ONLY_IF_CONNECTED";
      case 0x4e4:
switchD_005c0604_caseD_800704e4:
        return (int)"ERROR_OVERRIDE_NOCHANGES";
      case 0x4e5:
switchD_005c0604_caseD_800704e5:
        return (int)"ERROR_BAD_USER_PROFILE";
      case 0x4e6:
switchD_005c0604_caseD_800704e6:
        return (int)"ERROR_NOT_SUPPORTED_ON_SBS";
      case 0x4e7:
switchD_005c0604_caseD_800704e7:
        return (int)"ERROR_SERVER_SHUTDOWN_IN_PROGRESS";
      case 0x4e8:
switchD_005c0604_caseD_800704e8:
        return (int)"ERROR_HOST_DOWN";
      case 0x4e9:
switchD_005c0604_caseD_800704e9:
        return (int)"ERROR_NON_ACCOUNT_SID";
      case 0x4ea:
switchD_005c0604_caseD_800704ea:
        return (int)"ERROR_NON_DOMAIN_SID";
      case 0x4eb:
switchD_005c0604_caseD_800704eb:
        return (int)"ERROR_APPHELP_BLOCK";
      case 0x4ec:
switchD_005c0604_caseD_800704ec:
        return (int)"ERROR_ACCESS_DISABLED_BY_POLICY";
      case 0x4ed:
switchD_005c0604_caseD_800704ed:
        return (int)"ERROR_REG_NAT_CONSUMPTION";
      case 0x4ee:
switchD_005c0604_caseD_800704ee:
        return (int)"ERROR_CSCSHARE_OFFLINE";
      case 0x4ef:
switchD_005c0604_caseD_800704ef:
        return (int)"ERROR_PKINIT_FAILURE";
      case 0x4f0:
switchD_005c0604_caseD_800704f0:
        return (int)"ERROR_SMARTCARD_SUBSYSTEM_FAILURE";
      case 0x4f1:
switchD_005c0604_caseD_800704f1:
        return (int)"ERROR_DOWNGRADE_DETECTED";
      case 0x4f2:
        return (int)"SEC_E_SMARTCARD_CERT_REVOKED";
      case 0x4f3:
        return (int)"SEC_E_ISSUING_CA_UNTRUSTED";
      case 0x4f4:
        return (int)"SEC_E_REVOCATION_OFFLINE_C";
      case 0x4f5:
        return (int)"SEC_E_PKINIT_CLIENT_FAILURE";
      case 0x4f6:
        return (int)"SEC_E_SMARTCARD_CERT_EXPIRED";
      case 0x4f7:
switchD_005c0604_caseD_800704f7:
        return (int)"ERROR_MACHINE_LOCKED";
      case 0x4f9:
switchD_005c0604_caseD_800704f9:
        return (int)"ERROR_CALLBACK_SUPPLIED_INVALID_DATA";
      case 0x4fa:
switchD_005c0604_caseD_800704fa:
        return (int)"ERROR_SYNC_FOREGROUND_REFRESH_REQUIRED";
      case 0x4fb:
switchD_005c0604_caseD_800704fb:
        return (int)"ERROR_DRIVER_BLOCKED";
      case 0x4fc:
switchD_005c0604_caseD_800704fc:
        return (int)"ERROR_INVALID_IMPORT_OF_NON_DLL";
      case 0x4fd:
switchD_005c0604_caseD_800704fd:
        return (int)"ERROR_ACCESS_DISABLED_WEBBLADE";
      case 0x4fe:
switchD_005c0604_caseD_800704fe:
        return (int)"ERROR_ACCESS_DISABLED_WEBBLADE_TAMPER";
      case 0x4ff:
switchD_005c0604_caseD_800704ff:
        return (int)"ERROR_RECOVERY_FAILURE";
      case 0x500:
switchD_005c0604_caseD_80070500:
        return (int)"ERROR_ALREADY_FIBER";
      case 0x501:
switchD_005c0604_caseD_80070501:
        return (int)"ERROR_ALREADY_THREAD";
      case 0x502:
switchD_005c0604_caseD_80070502:
        return (int)"ERROR_STACK_BUFFER_OVERRUN";
      case 0x503:
switchD_005c0604_caseD_80070503:
        return (int)"ERROR_PARAMETER_QUOTA_EXCEEDED";
      case 0x504:
switchD_005c0604_caseD_80070504:
        return (int)"ERROR_DEBUGGER_INACTIVE";
      case 0x505:
switchD_005c0604_caseD_80070505:
        return (int)"ERROR_DELAY_LOAD_FAILED";
      case 0x514:
switchD_005c0604_caseD_80070514:
        return (int)"ERROR_NOT_ALL_ASSIGNED";
      case 0x515:
switchD_005c0604_caseD_80070515:
        return (int)"ERROR_SOME_NOT_MAPPED";
      case 0x516:
switchD_005c0604_caseD_80070516:
        return (int)"ERROR_NO_QUOTAS_FOR_ACCOUNT";
      case 0x517:
switchD_005c0604_caseD_80070517:
        return (int)"ERROR_LOCAL_USER_SESSION_KEY";
      case 0x518:
LAB_005c9c66:
        return 0x600000;
      case 0x519:
switchD_005c0604_caseD_80070519:
        return (int)"ERROR_UNKNOWN_REVISION";
      case 0x51a:
switchD_005c0604_caseD_8007051a:
        return (int)"ERROR_REVISION_MISMATCH";
      case 0x51b:
switchD_005c0604_caseD_8007051b:
        return (int)"ERROR_INVALID_OWNER";
      case 0x51c:
switchD_005c0604_caseD_8007051c:
        return (int)"ERROR_INVALID_PRIMARY_GROUP";
      case 0x51d:
switchD_005c0604_caseD_8007051d:
        return (int)"ERROR_NO_IMPERSONATION_TOKEN";
      case 0x51e:
switchD_005c0604_caseD_8007051e:
        return (int)"ERROR_CANT_DISABLE_MANDATORY";
      case 0x51f:
switchD_005c0604_caseD_8007051f:
        return (int)"ERROR_NO_LOGON_SERVERS";
      case 0x520:
switchD_005c0604_caseD_80070520:
        return (int)"ERROR_NO_SUCH_LOGON_SESSION";
      case 0x521:
switchD_005c0604_caseD_80070521:
        return (int)"ERROR_NO_SUCH_PRIVILEGE";
      case 0x522:
switchD_005c0604_caseD_80070522:
        return (int)"ERROR_PRIVILEGE_NOT_HELD";
      case 0x523:
switchD_005c0604_caseD_80070523:
        return (int)"ERROR_INVALID_ACCOUNT_NAME";
      case 0x524:
switchD_005c0604_caseD_80070524:
        return (int)"ERROR_USER_EXISTS";
      case 0x525:
switchD_005c0604_caseD_80070525:
        return (int)"ERROR_NO_SUCH_USER";
      case 0x526:
switchD_005c0604_caseD_80070526:
        return (int)"ERROR_GROUP_EXISTS";
      case 0x527:
switchD_005c0604_caseD_80070527:
        return (int)"ERROR_NO_SUCH_GROUP";
      case 0x528:
switchD_005c0604_caseD_80070528:
        return (int)"ERROR_MEMBER_IN_GROUP";
      case 0x529:
switchD_005c0604_caseD_80070529:
        return (int)"ERROR_MEMBER_NOT_IN_GROUP";
      case 0x52a:
switchD_005c0604_caseD_8007052a:
        return (int)"ERROR_LAST_ADMIN";
      case 0x52b:
switchD_005c0604_caseD_8007052b:
        return (int)"ERROR_WRONG_PASSWORD";
      case 0x52c:
switchD_005c0604_caseD_8007052c:
        return (int)"ERROR_ILL_FORMED_PASSWORD";
      case 0x52d:
switchD_005c0604_caseD_8007052d:
        return (int)"ERROR_PASSWORD_RESTRICTION";
      case 0x52e:
switchD_005c0604_caseD_8007052e:
        return (int)"ERROR_LOGON_FAILURE";
      case 0x52f:
switchD_005c0604_caseD_8007052f:
        return (int)"ERROR_ACCOUNT_RESTRICTION";
      case 0x530:
switchD_005c0604_caseD_80070530:
        return (int)"ERROR_INVALID_LOGON_HOURS";
      case 0x531:
switchD_005c0604_caseD_80070531:
        return (int)"ERROR_INVALID_WORKSTATION";
      case 0x532:
switchD_005c0604_caseD_80070532:
        return (int)"ERROR_PASSWORD_EXPIRED";
      case 0x533:
switchD_005c0604_caseD_80070533:
        return (int)"ERROR_ACCOUNT_DISABLED";
      case 0x534:
switchD_005c0604_caseD_80070534:
        return (int)"ERROR_NONE_MAPPED";
      case 0x535:
switchD_005c0604_caseD_80070535:
        return (int)"ERROR_TOO_MANY_LUIDS_REQUESTED";
      case 0x536:
switchD_005c0604_caseD_80070536:
        return (int)"ERROR_LUIDS_EXHAUSTED";
      case 0x537:
switchD_005c0604_caseD_80070537:
        return (int)"ERROR_INVALID_SUB_AUTHORITY";
      case 0x538:
switchD_005c0604_caseD_80070538:
        return (int)"ERROR_INVALID_ACL";
      case 0x539:
switchD_005c0604_caseD_80070539:
        return (int)"ERROR_INVALID_SID";
      case 0x53a:
switchD_005c0604_caseD_8007053a:
        return (int)"ERROR_INVALID_SECURITY_DESCR";
      case 0x53c:
switchD_005c0604_caseD_8007053c:
        return (int)"ERROR_BAD_INHERITANCE_ACL";
      case 0x53d:
switchD_005c0604_caseD_8007053d:
        return (int)"ERROR_SERVER_DISABLED";
      case 0x53e:
switchD_005c0604_caseD_8007053e:
        return (int)"ERROR_SERVER_NOT_DISABLED";
      case 0x53f:
switchD_005c0604_caseD_8007053f:
        return (int)"ERROR_INVALID_ID_AUTHORITY";
      case 0x540:
switchD_005c0604_caseD_80070540:
        return (int)"ERROR_ALLOTTED_SPACE_EXCEEDED";
      case 0x541:
switchD_005c0604_caseD_80070541:
        return (int)"ERROR_INVALID_GROUP_ATTRIBUTES";
      case 0x542:
switchD_005c0604_caseD_80070542:
        return (int)"ERROR_BAD_IMPERSONATION_LEVEL";
      case 0x543:
switchD_005c0604_caseD_80070543:
        return (int)"ERROR_CANT_OPEN_ANONYMOUS";
      case 0x544:
switchD_005c0604_caseD_80070544:
        return (int)"ERROR_BAD_VALIDATION_CLASS";
      case 0x545:
switchD_005c0604_caseD_80070545:
        return (int)"ERROR_BAD_TOKEN_TYPE";
      case 0x546:
switchD_005c0604_caseD_80070546:
        return (int)"ERROR_NO_SECURITY_ON_OBJECT";
      case 0x547:
switchD_005c0604_caseD_80070547:
        return (int)"ERROR_CANT_ACCESS_DOMAIN_INFO";
      case 0x548:
switchD_005c0604_caseD_80070548:
        return (int)"ERROR_INVALID_SERVER_STATE";
      case 0x549:
switchD_005c0604_caseD_80070549:
        return (int)"ERROR_INVALID_DOMAIN_STATE";
      case 0x54a:
switchD_005c0604_caseD_8007054a:
        return (int)"ERROR_INVALID_DOMAIN_ROLE";
      case 0x54b:
switchD_005c0604_caseD_8007054b:
        return (int)"ERROR_NO_SUCH_DOMAIN";
      case 0x54c:
switchD_005c0604_caseD_8007054c:
        return (int)"ERROR_DOMAIN_EXISTS";
      case 0x54d:
switchD_005c0604_caseD_8007054d:
        return (int)"ERROR_DOMAIN_LIMIT_EXCEEDED";
      case 0x54e:
switchD_005c0604_caseD_8007054e:
        return (int)"ERROR_INTERNAL_DB_CORRUPTION";
      case 0x54f:
switchD_005c0604_caseD_8007054f:
        return (int)"ERROR_INTERNAL_ERROR";
      case 0x550:
switchD_005c0604_caseD_80070550:
        return (int)"ERROR_GENERIC_NOT_MAPPED";
      case 0x551:
switchD_005c0604_caseD_80070551:
        return (int)"ERROR_BAD_DESCRIPTOR_FORMAT";
      case 0x552:
switchD_005c0604_caseD_80070552:
        return (int)"ERROR_NOT_LOGON_PROCESS";
      case 0x553:
switchD_005c5350_caseD_553:
        return (int)"ERROR_LOGON_SESSION_EXISTS";
      case 0x554:
switchD_005c061b_caseD_80070554:
        return (int)"ERROR_NO_SUCH_PACKAGE";
      case 0x555:
switchD_005c061b_caseD_80070555:
        return (int)"ERROR_BAD_LOGON_SESSION_STATE";
      case 0x556:
switchD_005c061b_caseD_80070556:
        return (int)"ERROR_LOGON_SESSION_COLLISION";
      case 0x557:
switchD_005c061b_caseD_80070557:
        return (int)"ERROR_INVALID_LOGON_TYPE";
      case 0x558:
switchD_005c061b_caseD_80070558:
        return (int)"ERROR_CANNOT_IMPERSONATE";
      case 0x559:
switchD_005c061b_caseD_80070559:
        return (int)"ERROR_RXACT_INVALID_STATE";
      case 0x55a:
switchD_005c061b_caseD_8007055a:
        return (int)"ERROR_RXACT_COMMIT_FAILURE";
      case 0x55b:
switchD_005c061b_caseD_8007055b:
        return (int)"ERROR_SPECIAL_ACCOUNT";
      case 0x55c:
switchD_005c061b_caseD_8007055c:
        return (int)"ERROR_SPECIAL_GROUP";
      case 0x55d:
switchD_005c061b_caseD_8007055d:
        return (int)"ERROR_SPECIAL_USER";
      case 0x55e:
switchD_005c061b_caseD_8007055e:
        return (int)"ERROR_MEMBERS_PRIMARY_GROUP";
      case 0x55f:
switchD_005c061b_caseD_8007055f:
        return (int)"ERROR_TOKEN_ALREADY_IN_USE";
      case 0x560:
switchD_005c061b_caseD_80070560:
        return (int)"ERROR_NO_SUCH_ALIAS";
      case 0x561:
switchD_005c061b_caseD_80070561:
        return (int)"ERROR_MEMBER_NOT_IN_ALIAS";
      case 0x562:
switchD_005c061b_caseD_80070562:
        return (int)"ERROR_MEMBER_IN_ALIAS";
      case 0x563:
switchD_005c061b_caseD_80070563:
        return (int)"ERROR_ALIAS_EXISTS";
      case 0x564:
switchD_005c061b_caseD_80070564:
        return (int)"ERROR_LOGON_NOT_GRANTED";
      case 0x565:
switchD_005c061b_caseD_80070565:
        return (int)"ERROR_TOO_MANY_SECRETS";
      case 0x566:
switchD_005c061b_caseD_80070566:
        return (int)"ERROR_SECRET_TOO_LONG";
      case 0x567:
switchD_005c061b_caseD_80070567:
        return (int)"ERROR_INTERNAL_DB_ERROR";
      case 0x568:
switchD_005c061b_caseD_80070568:
        return (int)"ERROR_TOO_MANY_CONTEXT_IDS";
      case 0x569:
switchD_005c061b_caseD_80070569:
        return (int)"ERROR_LOGON_TYPE_NOT_GRANTED";
      case 0x56a:
switchD_005c061b_caseD_8007056a:
        return (int)"ERROR_NT_CROSS_ENCRYPTION_REQUIRED";
      case 0x56b:
switchD_005c061b_caseD_8007056b:
        return (int)"ERROR_NO_SUCH_MEMBER";
      case 0x56c:
switchD_005c061b_caseD_8007056c:
        return (int)"ERROR_INVALID_MEMBER";
      case 0x56d:
switchD_005c061b_caseD_8007056d:
        return (int)"ERROR_TOO_MANY_SIDS";
      case 0x56e:
switchD_005c061b_caseD_8007056e:
        return (int)"ERROR_LM_CROSS_ENCRYPTION_REQUIRED";
      case 0x56f:
switchD_005c061b_caseD_8007056f:
        return (int)"ERROR_NO_INHERITANCE";
      case 0x570:
switchD_005c061b_caseD_80070570:
        return (int)"ERROR_FILE_CORRUPT";
      case 0x571:
switchD_005c061b_caseD_80070571:
        return (int)"ERROR_DISK_CORRUPT";
      case 0x572:
switchD_005c061b_caseD_80070572:
        return (int)"ERROR_NO_USER_SESSION_KEY";
      case 0x573:
switchD_005c061b_caseD_80070573:
        return (int)"ERROR_LICENSE_QUOTA_EXCEEDED";
      case 0x574:
switchD_005c061b_caseD_80070574:
        return (int)"ERROR_WRONG_TARGET_NAME";
      case 0x575:
switchD_005c061b_caseD_80070575:
        return (int)"ERROR_MUTUAL_AUTH_FAILED";
      case 0x576:
switchD_005c061b_caseD_80070576:
        return (int)"ERROR_TIME_SKEW";
      case 0x577:
switchD_005c061b_caseD_80070577:
        return (int)"ERROR_CURRENT_DOMAIN_NOT_ALLOWED";
      case 0x578:
switchD_005c061b_caseD_80070578:
        return (int)"ERROR_INVALID_WINDOW_HANDLE";
      case 0x579:
switchD_005c061b_caseD_80070579:
        return (int)"ERROR_INVALID_MENU_HANDLE";
      case 0x57a:
switchD_005c061b_caseD_8007057a:
        return (int)"ERROR_INVALID_CURSOR_HANDLE";
      case 0x57b:
switchD_005c061b_caseD_8007057b:
        return (int)"ERROR_INVALID_ACCEL_HANDLE";
      case 0x57c:
switchD_005c061b_caseD_8007057c:
        return (int)"ERROR_INVALID_HOOK_HANDLE";
      case 0x57d:
switchD_005c061b_caseD_8007057d:
        return (int)"ERROR_INVALID_DWP_HANDLE";
      case 0x57e:
switchD_005c061b_caseD_8007057e:
        return (int)"ERROR_TLW_WITH_WSCHILD";
      case 0x57f:
switchD_005c061b_caseD_8007057f:
        return (int)"ERROR_CANNOT_FIND_WND_CLASS";
      case 0x580:
switchD_005c061b_caseD_80070580:
        return (int)"ERROR_WINDOW_OF_OTHER_THREAD";
      case 0x581:
switchD_005c061b_caseD_80070581:
        return (int)"ERROR_HOTKEY_ALREADY_REGISTERED";
      case 0x582:
switchD_005c061b_caseD_80070582:
        return (int)"ERROR_CLASS_ALREADY_EXISTS";
      case 0x583:
switchD_005c061b_caseD_80070583:
        return (int)"ERROR_CLASS_DOES_NOT_EXIST";
      case 0x584:
switchD_005c061b_caseD_80070584:
        return (int)"ERROR_CLASS_HAS_WINDOWS";
      case 0x585:
switchD_005c061b_caseD_80070585:
        return (int)"ERROR_INVALID_INDEX";
      case 0x586:
switchD_005c061b_caseD_80070586:
        return (int)"ERROR_INVALID_ICON_HANDLE";
      case 0x587:
switchD_005c061b_caseD_80070587:
        return (int)"ERROR_PRIVATE_DIALOG_INDEX";
      case 0x588:
switchD_005c061b_caseD_80070588:
        return (int)"ERROR_LISTBOX_ID_NOT_FOUND";
      case 0x589:
switchD_005c061b_caseD_80070589:
        return (int)"ERROR_NO_WILDCARD_CHARACTERS";
      case 0x58a:
switchD_005c061b_caseD_8007058a:
        return (int)"ERROR_CLIPBOARD_NOT_OPEN";
      case 0x58b:
switchD_005c061b_caseD_8007058b:
        return (int)"ERROR_HOTKEY_NOT_REGISTERED";
      case 0x58c:
switchD_005c061b_caseD_8007058c:
        return (int)"ERROR_WINDOW_NOT_DIALOG";
      case 0x58d:
switchD_005c061b_caseD_8007058d:
        return (int)"ERROR_CONTROL_ID_NOT_FOUND";
      case 0x58e:
switchD_005c061b_caseD_8007058e:
        return (int)"ERROR_INVALID_COMBOBOX_MESSAGE";
      case 0x58f:
switchD_005c061b_caseD_8007058f:
        return (int)"ERROR_WINDOW_NOT_COMBOBOX";
      case 0x590:
switchD_005c061b_caseD_80070590:
        return (int)"ERROR_INVALID_EDIT_HEIGHT";
      case 0x591:
switchD_005c061b_caseD_80070591:
        return (int)"ERROR_DC_NOT_FOUND";
      case 0x592:
switchD_005c061b_caseD_80070592:
        return (int)"ERROR_INVALID_HOOK_FILTER";
      case 0x593:
switchD_005c061b_caseD_80070593:
        return (int)"ERROR_INVALID_FILTER_PROC";
      case 0x594:
switchD_005c061b_caseD_80070594:
        return (int)"ERROR_HOOK_NEEDS_HMOD";
      case 0x595:
switchD_005c061b_caseD_80070595:
        return (int)"ERROR_GLOBAL_ONLY_HOOK";
      case 0x596:
switchD_005c061b_caseD_80070596:
        return (int)"ERROR_JOURNAL_HOOK_SET";
      case 0x597:
switchD_005c061b_caseD_80070597:
        return (int)"ERROR_HOOK_NOT_INSTALLED";
      case 0x598:
switchD_005c061b_caseD_80070598:
        return (int)"ERROR_INVALID_LB_MESSAGE";
      case 0x599:
switchD_005c061b_caseD_80070599:
        return (int)"ERROR_SETCOUNT_ON_BAD_LB";
      case 0x59a:
switchD_005c061b_caseD_8007059a:
        return (int)"ERROR_LB_WITHOUT_TABSTOPS";
      case 0x59b:
switchD_005c061b_caseD_8007059b:
        return (int)"ERROR_DESTROY_OBJECT_OF_OTHER_THREAD";
      case 0x59c:
switchD_005c061b_caseD_8007059c:
        return (int)"ERROR_CHILD_WINDOW_MENU";
      case 0x59d:
switchD_005c061b_caseD_8007059d:
        return (int)"ERROR_NO_SYSTEM_MENU";
      case 0x59e:
switchD_005c061b_caseD_8007059e:
        return (int)"ERROR_INVALID_MSGBOX_STYLE";
      case 0x59f:
switchD_005c061b_caseD_8007059f:
        return (int)"ERROR_INVALID_SPI_VALUE";
      case 0x5a0:
switchD_005c061b_caseD_800705a0:
        return (int)"ERROR_SCREEN_ALREADY_LOCKED";
      case 0x5a1:
switchD_005c061b_caseD_800705a1:
        return (int)"ERROR_HWNDS_HAVE_DIFF_PARENT";
      case 0x5a2:
switchD_005c061b_caseD_800705a2:
        return (int)"ERROR_NOT_CHILD_WINDOW";
      case 0x5a3:
switchD_005c061b_caseD_800705a3:
        return (int)"ERROR_INVALID_GW_COMMAND";
      case 0x5a4:
switchD_005c061b_caseD_800705a4:
        return (int)"ERROR_INVALID_THREAD_ID";
      case 0x5a5:
switchD_005c061b_caseD_800705a5:
        return (int)"ERROR_NON_MDICHILD_WINDOW";
      case 0x5a6:
switchD_005c061b_caseD_800705a6:
        return (int)"ERROR_POPUP_ALREADY_ACTIVE";
      case 0x5a7:
switchD_005c061b_caseD_800705a7:
        return (int)"ERROR_NO_SCROLLBARS";
      case 0x5a8:
switchD_005c061b_caseD_800705a8:
        return (int)"ERROR_INVALID_SCROLLBAR_RANGE";
      case 0x5a9:
switchD_005c061b_caseD_800705a9:
        return (int)"ERROR_INVALID_SHOWWIN_COMMAND";
      case 0x5aa:
switchD_005c061b_caseD_800705aa:
        return (int)"ERROR_NO_SYSTEM_RESOURCES";
      case 0x5ab:
switchD_005c061b_caseD_800705ab:
        return (int)"ERROR_NONPAGED_SYSTEM_RESOURCES";
      case 0x5ac:
switchD_005c061b_caseD_800705ac:
        return (int)"ERROR_PAGED_SYSTEM_RESOURCES";
      case 0x5ad:
switchD_005c061b_caseD_800705ad:
        return (int)"ERROR_WORKING_SET_QUOTA";
      case 0x5ae:
switchD_005c061b_caseD_800705ae:
        return (int)"ERROR_PAGEFILE_QUOTA";
      case 0x5af:
switchD_005c061b_caseD_800705af:
        return (int)"ERROR_COMMITMENT_LIMIT";
      case 0x5b0:
switchD_005c061b_caseD_800705b0:
        return (int)"ERROR_MENU_ITEM_NOT_FOUND";
      case 0x5b1:
switchD_005c061b_caseD_800705b1:
        return (int)"ERROR_INVALID_KEYBOARD_HANDLE";
      case 0x5b2:
switchD_005c061b_caseD_800705b2:
        return (int)"ERROR_HOOK_TYPE_NOT_ALLOWED";
      case 0x5b3:
switchD_005c061b_caseD_800705b3:
        return (int)"ERROR_REQUIRES_INTERACTIVE_WINDOWSTATION";
      case 0x5b4:
switchD_005c061b_caseD_800705b4:
        return (int)"ERROR_TIMEOUT";
      case 0x5b5:
switchD_005c061b_caseD_800705b5:
        return (int)"ERROR_INVALID_MONITOR_HANDLE";
      case 0x5dc:
switchD_005c061b_caseD_800705dc:
        return (int)"ERROR_EVENTLOG_FILE_CORRUPT";
      case 0x5dd:
switchD_005c061b_caseD_800705dd:
        return (int)"ERROR_EVENTLOG_CANT_START";
      case 0x5de:
switchD_005c061b_caseD_800705de:
        return (int)"ERROR_LOG_FILE_FULL";
      case 0x5df:
switchD_005c061b_caseD_800705df:
        return (int)"ERROR_EVENTLOG_FILE_CHANGED";
      case 0x641:
switchD_005c061b_caseD_80070641:
        return (int)"ERROR_INSTALL_SERVICE_FAILURE";
      case 0x642:
switchD_005c061b_caseD_80070642:
        return (int)"ERROR_INSTALL_USEREXIT";
      case 0x643:
switchD_005c061b_caseD_80070643:
        return (int)"ERROR_INSTALL_FAILURE";
      case 0x644:
switchD_005c061b_caseD_80070644:
        return (int)"ERROR_INSTALL_SUSPEND";
      case 0x645:
switchD_005c061b_caseD_80070645:
        return (int)"ERROR_UNKNOWN_PRODUCT";
      case 0x646:
switchD_005c061b_caseD_80070646:
        return (int)"ERROR_UNKNOWN_FEATURE";
      case 0x647:
switchD_005c061b_caseD_80070647:
        return (int)"ERROR_UNKNOWN_COMPONENT";
      case 0x648:
switchD_005c061b_caseD_80070648:
        return (int)"ERROR_UNKNOWN_PROPERTY";
      case 0x649:
switchD_005c061b_caseD_80070649:
        return (int)"ERROR_INVALID_HANDLE_STATE";
      case 0x64a:
switchD_005c061b_caseD_8007064a:
        return (int)"ERROR_BAD_CONFIGURATION";
      case 0x64b:
switchD_005c061b_caseD_8007064b:
        return (int)"ERROR_INDEX_ABSENT";
      case 0x64c:
switchD_005c061b_caseD_8007064c:
        return (int)"ERROR_INSTALL_SOURCE_ABSENT";
      case 0x64d:
switchD_005c061b_caseD_8007064d:
        return (int)"ERROR_INSTALL_PACKAGE_VERSION";
      case 0x64e:
switchD_005c061b_caseD_8007064e:
        return (int)"ERROR_PRODUCT_UNINSTALLED";
      case 0x64f:
switchD_005c061b_caseD_8007064f:
        return (int)"ERROR_BAD_QUERY_SYNTAX";
      case 0x650:
switchD_005c061b_caseD_80070650:
        return (int)"ERROR_INVALID_FIELD";
      case 0x651:
switchD_005c061b_caseD_80070651:
        return (int)"ERROR_DEVICE_REMOVED";
      case 0x652:
switchD_005c061b_caseD_80070652:
        return (int)"ERROR_INSTALL_ALREADY_RUNNING";
      case 0x653:
switchD_005c061b_caseD_80070653:
        return (int)"ERROR_INSTALL_PACKAGE_OPEN_FAILED";
      case 0x654:
switchD_005c061b_caseD_80070654:
        return (int)"ERROR_INSTALL_PACKAGE_INVALID";
      case 0x655:
switchD_005c061b_caseD_80070655:
        return (int)"ERROR_INSTALL_UI_FAILURE";
      case 0x656:
switchD_005c061b_caseD_80070656:
        return (int)"ERROR_INSTALL_LOG_FAILURE";
      case 0x657:
switchD_005c061b_caseD_80070657:
        return (int)"ERROR_INSTALL_LANGUAGE_UNSUPPORTED";
      case 0x658:
switchD_005c061b_caseD_80070658:
        return (int)"ERROR_INSTALL_TRANSFORM_FAILURE";
      case 0x659:
switchD_005c061b_caseD_80070659:
        return (int)"ERROR_INSTALL_PACKAGE_REJECTED";
      case 0x65a:
switchD_005c061b_caseD_8007065a:
        return (int)"ERROR_FUNCTION_NOT_CALLED";
      case 0x65b:
switchD_005c061b_caseD_8007065b:
        return (int)"ERROR_FUNCTION_FAILED";
      case 0x65c:
switchD_005c061b_caseD_8007065c:
        return (int)"ERROR_INVALID_TABLE";
      case 0x65d:
switchD_005c061b_caseD_8007065d:
        return (int)"ERROR_DATATYPE_MISMATCH";
      case 0x65e:
switchD_005c061b_caseD_8007065e:
        return (int)"ERROR_UNSUPPORTED_TYPE";
      case 0x65f:
switchD_005c061b_caseD_8007065f:
        return (int)"ERROR_CREATE_FAILED";
      case 0x660:
switchD_005c061b_caseD_80070660:
        return (int)"ERROR_INSTALL_TEMP_UNWRITABLE";
      case 0x661:
switchD_005c061b_caseD_80070661:
        return (int)"ERROR_INSTALL_PLATFORM_UNSUPPORTED";
      case 0x662:
switchD_005c061b_caseD_80070662:
        return (int)"ERROR_INSTALL_NOTUSED";
      case 0x663:
switchD_005c061b_caseD_80070663:
        return (int)"ERROR_PATCH_PACKAGE_OPEN_FAILED";
      case 0x664:
switchD_005c061b_caseD_80070664:
        return (int)"ERROR_PATCH_PACKAGE_INVALID";
      case 0x665:
switchD_005c061b_caseD_80070665:
        return (int)"ERROR_PATCH_PACKAGE_UNSUPPORTED";
      case 0x666:
switchD_005c061b_caseD_80070666:
        return (int)"ERROR_PRODUCT_VERSION";
      case 0x667:
switchD_005c061b_caseD_80070667:
        return (int)"ERROR_INVALID_COMMAND_LINE";
      case 0x668:
switchD_005c061b_caseD_80070668:
        return (int)"ERROR_INSTALL_REMOTE_DISALLOWED";
      case 0x669:
switchD_005c061b_caseD_80070669:
        return (int)"ERROR_SUCCESS_REBOOT_INITIATED";
      case 0x66a:
switchD_005c061b_caseD_8007066a:
        return (int)"ERROR_PATCH_TARGET_NOT_FOUND";
      case 0x66b:
switchD_005c061b_caseD_8007066b:
        return (int)"ERROR_PATCH_PACKAGE_REJECTED";
      case 0x66c:
switchD_005c061b_caseD_8007066c:
        return (int)"ERROR_INSTALL_TRANSFORM_REJECTED";
      case 0x66d:
switchD_005c061b_caseD_8007066d:
        return (int)"ERROR_INSTALL_REMOTE_PROHIBITED";
      case 0x6a4:
switchD_005c061b_caseD_800706a4:
        return (int)"RPC_S_INVALID_STRING_BINDING";
      case 0x6a5:
switchD_005c061b_caseD_800706a5:
        return (int)"RPC_S_WRONG_KIND_OF_BINDING";
      case 0x6a6:
switchD_005c061b_caseD_800706a6:
        return (int)"RPC_S_INVALID_BINDING";
      case 0x6a7:
switchD_005c061b_caseD_800706a7:
        return (int)"RPC_S_PROTSEQ_NOT_SUPPORTED";
      case 0x6a8:
switchD_005c061b_caseD_800706a8:
        return (int)"RPC_S_INVALID_RPC_PROTSEQ";
      }
    }
  }
  else if (in_stack_00000004 < 0x8cb) {
    if (in_stack_00000004 == 0x8ca) {
LAB_005c679c:
      return (int)"ERROR_NOT_CONNECTED";
    }
    switch(in_stack_00000004) {
    case 0x6aa:
switchD_005c061b_caseD_800706aa:
      return (int)"RPC_S_INVALID_ENDPOINT_FORMAT";
    case 0x6ab:
switchD_005c061b_caseD_800706ab:
      return (int)"RPC_S_INVALID_NET_ADDR";
    case 0x6ac:
switchD_005c061b_caseD_800706ac:
      return (int)"RPC_S_NO_ENDPOINT_FOUND";
    case 0x6ad:
switchD_005c061b_caseD_800706ad:
      return (int)"RPC_S_INVALID_TIMEOUT";
    case 0x6ae:
switchD_005c061b_caseD_800706ae:
      return (int)"RPC_S_OBJECT_NOT_FOUND";
    case 0x6af:
switchD_005c061b_caseD_800706af:
      return (int)"RPC_S_ALREADY_REGISTERED";
    case 0x6b0:
switchD_005c061b_caseD_800706b0:
      return (int)"RPC_S_TYPE_ALREADY_REGISTERED";
    case 0x6b1:
switchD_005c061b_caseD_800706b1:
      return (int)"RPC_S_ALREADY_LISTENING";
    case 0x6b2:
switchD_005c061b_caseD_800706b2:
      return (int)"RPC_S_NO_PROTSEQS_REGISTERED";
    case 0x6b3:
switchD_005c061b_caseD_800706b3:
      return (int)"RPC_S_NOT_LISTENING";
    case 0x6b4:
switchD_005c061b_caseD_800706b4:
      return (int)"RPC_S_UNKNOWN_MGR_TYPE";
    case 0x6b5:
switchD_005c061b_caseD_800706b5:
      return (int)"RPC_S_UNKNOWN_IF";
    case 0x6b6:
switchD_005c061b_caseD_800706b6:
      return (int)"RPC_S_NO_BINDINGS";
    case 0x6b7:
switchD_005c061b_caseD_800706b7:
      return (int)"RPC_S_NO_PROTSEQS";
    case 0x6b8:
switchD_005c061b_caseD_800706b8:
      return (int)"RPC_S_CANT_CREATE_ENDPOINT";
    case 0x6b9:
switchD_005c061b_caseD_800706b9:
      return (int)"RPC_S_OUT_OF_RESOURCES";
    case 0x6ba:
switchD_005c061b_caseD_800706ba:
      return (int)"RPC_S_SERVER_UNAVAILABLE";
    case 0x6bb:
switchD_005c061b_caseD_800706bb:
      return (int)"RPC_S_SERVER_TOO_BUSY";
    case 0x6bc:
switchD_005c061b_caseD_800706bc:
      return (int)"RPC_S_INVALID_NETWORK_OPTIONS";
    case 0x6bd:
switchD_005c061b_caseD_800706bd:
      return (int)"RPC_S_NO_CALL_ACTIVE";
    case 0x6be:
switchD_005c061b_caseD_800706be:
      return (int)"RPC_S_CALL_FAILED";
    case 0x6bf:
switchD_005c061b_caseD_800706bf:
      return (int)"RPC_S_CALL_FAILED_DNE";
    case 0x6c0:
switchD_005c061b_caseD_800706c0:
      return (int)"RPC_S_PROTOCOL_ERROR";
    case 0x6c2:
switchD_005c061b_caseD_800706c2:
      return (int)"RPC_S_UNSUPPORTED_TRANS_SYN";
    case 0x6c4:
switchD_005c061b_caseD_800706c4:
      return (int)"RPC_S_UNSUPPORTED_TYPE";
    case 0x6c5:
switchD_005c061b_caseD_800706c5:
      return (int)"RPC_S_INVALID_TAG";
    case 0x6c6:
switchD_005c061b_caseD_800706c6:
      return (int)"RPC_S_INVALID_BOUND";
    case 0x6c7:
switchD_005c061b_caseD_800706c7:
      return (int)"RPC_S_NO_ENTRY_NAME";
    case 0x6c8:
switchD_005c061b_caseD_800706c8:
      return (int)"RPC_S_INVALID_NAME_SYNTAX";
    case 0x6c9:
switchD_005c061b_caseD_800706c9:
      return (int)"RPC_S_UNSUPPORTED_NAME_SYNTAX";
    case 0x6cb:
switchD_005c061b_caseD_800706cb:
      return (int)"RPC_S_UUID_NO_ADDRESS";
    case 0x6cc:
switchD_005c061b_caseD_800706cc:
      return (int)"RPC_S_DUPLICATE_ENDPOINT";
    case 0x6cd:
switchD_005c061b_caseD_800706cd:
      return (int)"RPC_S_UNKNOWN_AUTHN_TYPE";
    case 0x6ce:
switchD_005c061b_caseD_800706ce:
      return (int)"RPC_S_MAX_CALLS_TOO_SMALL";
    case 0x6cf:
switchD_005c061b_caseD_800706cf:
      return (int)"RPC_S_STRING_TOO_LONG";
    case 0x6d0:
switchD_005c061b_caseD_800706d0:
      return (int)"RPC_S_PROTSEQ_NOT_FOUND";
    case 0x6d1:
switchD_005c061b_caseD_800706d1:
      return (int)"RPC_S_PROCNUM_OUT_OF_RANGE";
    case 0x6d2:
switchD_005c061b_caseD_800706d2:
      return (int)"RPC_S_BINDING_HAS_NO_AUTH";
    case 0x6d3:
switchD_005c061b_caseD_800706d3:
      return (int)"RPC_S_UNKNOWN_AUTHN_SERVICE";
    case 0x6d4:
switchD_005c061b_caseD_800706d4:
      return (int)"RPC_S_UNKNOWN_AUTHN_LEVEL";
    case 0x6d5:
switchD_005c061b_caseD_800706d5:
      return (int)"RPC_S_INVALID_AUTH_IDENTITY";
    case 0x6d6:
switchD_005c061b_caseD_800706d6:
      return (int)"RPC_S_UNKNOWN_AUTHZ_SERVICE";
    case 0x6d7:
switchD_005c061b_caseD_800706d7:
      return (int)"EPT_S_INVALID_ENTRY";
    case 0x6d8:
switchD_005c061b_caseD_800706d8:
      return (int)"EPT_S_CANT_PERFORM_OP";
    case 0x6d9:
switchD_005c061b_caseD_800706d9:
      return (int)"EPT_S_NOT_REGISTERED";
    case 0x6da:
switchD_005c061b_caseD_800706da:
      return (int)"RPC_S_NOTHING_TO_EXPORT";
    case 0x6db:
switchD_005c061b_caseD_800706db:
      return (int)"RPC_S_INCOMPLETE_NAME";
    case 0x6dc:
switchD_005c061b_caseD_800706dc:
      return (int)"RPC_S_INVALID_VERS_OPTION";
    case 0x6dd:
switchD_005c061b_caseD_800706dd:
      return (int)"RPC_S_NO_MORE_MEMBERS";
    case 0x6de:
switchD_005c061b_caseD_800706de:
      return (int)"RPC_S_NOT_ALL_OBJS_UNEXPORTED";
    case 0x6df:
switchD_005c061b_caseD_800706df:
      return (int)"RPC_S_INTERFACE_NOT_FOUND";
    case 0x6e0:
switchD_005c061b_caseD_800706e0:
      return (int)"RPC_S_ENTRY_ALREADY_EXISTS";
    case 0x6e1:
switchD_005c061b_caseD_800706e1:
      return (int)"RPC_S_ENTRY_NOT_FOUND";
    case 0x6e2:
switchD_005c061b_caseD_800706e2:
      return (int)"RPC_S_NAME_SERVICE_UNAVAILABLE";
    case 0x6e3:
switchD_005c061b_caseD_800706e3:
      return (int)"RPC_S_INVALID_NAF_ID";
    case 0x6e4:
switchD_005c061b_caseD_800706e4:
      return (int)"RPC_S_CANNOT_SUPPORT";
    case 0x6e5:
switchD_005c061b_caseD_800706e5:
      return (int)"RPC_S_NO_CONTEXT_AVAILABLE";
    case 0x6e6:
switchD_005c061b_caseD_800706e6:
      return (int)"RPC_S_INTERNAL_ERROR";
    case 0x6e7:
switchD_005c061b_caseD_800706e7:
      return (int)"RPC_S_ZERO_DIVIDE";
    case 0x6e8:
switchD_005c061b_caseD_800706e8:
      return (int)"RPC_S_ADDRESS_ERROR";
    case 0x6e9:
switchD_005c061b_caseD_800706e9:
      return (int)"RPC_S_FP_DIV_ZERO";
    case 0x6ea:
switchD_005c061b_caseD_800706ea:
      return (int)"RPC_S_FP_UNDERFLOW";
    case 0x6eb:
switchD_005c061b_caseD_800706eb:
      return (int)"RPC_S_FP_OVERFLOW";
    case 0x6ec:
switchD_005c061b_caseD_800706ec:
      return (int)"RPC_X_NO_MORE_ENTRIES";
    case 0x6ed:
switchD_005c061b_caseD_800706ed:
      return (int)"RPC_X_SS_CHAR_TRANS_OPEN_FAIL";
    case 0x6ee:
switchD_005c061b_caseD_800706ee:
      return (int)"RPC_X_SS_CHAR_TRANS_SHORT_FILE";
    case 0x6ef:
switchD_005c061b_caseD_800706ef:
      return (int)"RPC_X_SS_IN_NULL_CONTEXT";
    case 0x6f1:
switchD_005c061b_caseD_800706f1:
      return (int)"RPC_X_SS_CONTEXT_DAMAGED";
    case 0x6f2:
switchD_005c061b_caseD_800706f2:
      return (int)"RPC_X_SS_HANDLES_MISMATCH";
    case 0x6f3:
switchD_005c061b_caseD_800706f3:
      return (int)"RPC_X_SS_CANNOT_GET_CALL_HANDLE";
    case 0x6f4:
switchD_005c061b_caseD_800706f4:
      return (int)"RPC_X_NULL_REF_POINTER";
    case 0x6f5:
switchD_005c061b_caseD_800706f5:
      return (int)"RPC_X_ENUM_VALUE_OUT_OF_RANGE";
    case 0x6f6:
switchD_005c061b_caseD_800706f6:
      return (int)"RPC_X_BYTE_COUNT_TOO_SMALL";
    case 0x6f7:
switchD_005c061b_caseD_800706f7:
      return (int)"RPC_X_BAD_STUB_DATA";
    case 0x6f8:
switchD_005c061b_caseD_800706f8:
      return (int)"ERROR_INVALID_USER_BUFFER";
    case 0x6f9:
switchD_005c061b_caseD_800706f9:
      return (int)"ERROR_UNRECOGNIZED_MEDIA";
    case 0x6fa:
switchD_005c061b_caseD_800706fa:
      return (int)"ERROR_NO_TRUST_LSA_SECRET";
    case 0x6fb:
switchD_005c061b_caseD_800706fb:
      return (int)"ERROR_NO_TRUST_SAM_ACCOUNT";
    case 0x6fc:
switchD_005c061b_caseD_800706fc:
      return (int)"ERROR_TRUSTED_DOMAIN_FAILURE";
    case 0x6fd:
switchD_005c061b_caseD_800706fd:
      return (int)"ERROR_TRUSTED_RELATIONSHIP_FAILURE";
    case 0x6fe:
switchD_005c061b_caseD_800706fe:
      return (int)"ERROR_TRUST_FAILURE";
    case 0x6ff:
switchD_005c061b_caseD_800706ff:
      return (int)"RPC_S_CALL_IN_PROGRESS";
    case 0x700:
switchD_005c061b_caseD_80070700:
      return (int)"ERROR_NETLOGON_NOT_STARTED";
    case 0x701:
switchD_005c061b_caseD_80070701:
      return (int)"ERROR_ACCOUNT_EXPIRED";
    case 0x702:
switchD_005c061b_caseD_80070702:
      return (int)"ERROR_REDIRECTOR_HAS_OPEN_HANDLES";
    case 0x703:
switchD_005c061b_caseD_80070703:
      return (int)"ERROR_PRINTER_DRIVER_ALREADY_INSTALLED";
    case 0x704:
switchD_005c061b_caseD_80070704:
      return (int)"ERROR_UNKNOWN_PORT";
    case 0x705:
switchD_005c061b_caseD_80070705:
      return (int)"ERROR_UNKNOWN_PRINTER_DRIVER";
    case 0x706:
switchD_005c061b_caseD_80070706:
      return (int)"ERROR_UNKNOWN_PRINTPROCESSOR";
    case 0x707:
switchD_005c061b_caseD_80070707:
      return (int)"ERROR_INVALID_SEPARATOR_FILE";
    case 0x708:
switchD_005c061b_caseD_80070708:
      return (int)"ERROR_INVALID_PRIORITY";
    case 0x709:
switchD_005c061b_caseD_80070709:
      return (int)"ERROR_INVALID_PRINTER_NAME";
    case 0x70a:
switchD_005c061b_caseD_8007070a:
      return (int)"ERROR_PRINTER_ALREADY_EXISTS";
    case 0x70b:
switchD_005c061b_caseD_8007070b:
      return (int)"ERROR_INVALID_PRINTER_COMMAND";
    case 0x70c:
switchD_005c061b_caseD_8007070c:
      return (int)"ERROR_INVALID_DATATYPE";
    case 0x70d:
switchD_005c061b_caseD_8007070d:
      return (int)"ERROR_INVALID_ENVIRONMENT";
    case 0x70e:
switchD_005c061b_caseD_8007070e:
      return (int)"RPC_S_NO_MORE_BINDINGS";
    case 0x70f:
switchD_005c061b_caseD_8007070f:
      return (int)"ERROR_NOLOGON_INTERDOMAIN_TRUST_ACCOUNT";
    case 0x710:
switchD_005c061b_caseD_80070710:
      return (int)"ERROR_NOLOGON_WORKSTATION_TRUST_ACCOUNT";
    case 0x711:
switchD_005c061b_caseD_80070711:
      return (int)"ERROR_NOLOGON_SERVER_TRUST_ACCOUNT";
    case 0x712:
switchD_005c061b_caseD_80070712:
      return (int)"ERROR_DOMAIN_TRUST_INCONSISTENT";
    case 0x713:
switchD_005c061b_caseD_80070713:
      return (int)"ERROR_SERVER_HAS_OPEN_HANDLES";
    case 0x714:
switchD_005c061b_caseD_80070714:
      return (int)"ERROR_RESOURCE_DATA_NOT_FOUND";
    case 0x715:
switchD_005c061b_caseD_80070715:
      return (int)"ERROR_RESOURCE_TYPE_NOT_FOUND";
    case 0x716:
switchD_005c061b_caseD_80070716:
      return (int)"ERROR_RESOURCE_NAME_NOT_FOUND";
    case 0x717:
switchD_005c061b_caseD_80070717:
      return (int)"ERROR_RESOURCE_LANG_NOT_FOUND";
    case 0x718:
switchD_005c061b_caseD_80070718:
      return (int)"ERROR_NOT_ENOUGH_QUOTA";
    case 0x719:
switchD_005c061b_caseD_80070719:
      return (int)"RPC_S_NO_INTERFACES";
    case 0x71a:
switchD_005c061b_caseD_8007071a:
      return (int)"RPC_S_CALL_CANCELLED";
    case 0x71b:
switchD_005c061b_caseD_8007071b:
      return (int)"RPC_S_BINDING_INCOMPLETE";
    case 0x71c:
switchD_005c061b_caseD_8007071c:
      return (int)"RPC_S_COMM_FAILURE";
    case 0x71d:
switchD_005c061b_caseD_8007071d:
      return (int)"RPC_S_UNSUPPORTED_AUTHN_LEVEL";
    case 0x71e:
switchD_005c061b_caseD_8007071e:
      return (int)"RPC_S_NO_PRINC_NAME";
    case 0x71f:
switchD_005c061b_caseD_8007071f:
      return (int)"RPC_S_NOT_RPC_ERROR";
    case 0x720:
switchD_005c061b_caseD_80070720:
      return (int)"RPC_S_UUID_LOCAL_ONLY";
    case 0x721:
switchD_005c061b_caseD_80070721:
      return (int)"RPC_S_SEC_PKG_ERROR";
    case 0x722:
switchD_005c061b_caseD_80070722:
      return (int)"RPC_S_NOT_CANCELLED";
    case 0x723:
switchD_005c061b_caseD_80070723:
      return (int)"RPC_X_INVALID_ES_ACTION";
    case 0x724:
switchD_005c061b_caseD_80070724:
      return (int)"RPC_X_WRONG_ES_VERSION";
    case 0x725:
switchD_005c061b_caseD_80070725:
      return (int)"RPC_X_WRONG_STUB_VERSION";
    case 0x726:
switchD_005c061b_caseD_80070726:
      return (int)"RPC_X_INVALID_PIPE_OBJECT";
    case 0x727:
switchD_005c061b_caseD_80070727:
      return (int)"RPC_X_WRONG_PIPE_ORDER";
    case 0x728:
switchD_005c061b_caseD_80070728:
      return (int)"RPC_X_WRONG_PIPE_VERSION";
    case 0x76a:
switchD_005c061b_caseD_8007076a:
      return (int)"RPC_S_GROUP_MEMBER_NOT_FOUND";
    case 0x76b:
switchD_005c061b_caseD_8007076b:
      return (int)"EPT_S_CANT_CREATE";
    case 0x76c:
switchD_005c061b_caseD_8007076c:
      return (int)"RPC_S_INVALID_OBJECT";
    case 0x76d:
switchD_005c061b_caseD_8007076d:
      return (int)"ERROR_INVALID_TIME";
    case 0x76e:
switchD_005c061b_caseD_8007076e:
      return (int)"ERROR_INVALID_FORM_NAME";
    case 0x76f:
switchD_005c061b_caseD_8007076f:
      return (int)"ERROR_INVALID_FORM_SIZE";
    case 0x770:
switchD_005c061b_caseD_80070770:
      return (int)"ERROR_ALREADY_WAITING";
    case 0x771:
switchD_005c061b_caseD_80070771:
      return (int)"ERROR_PRINTER_DELETED";
    case 0x772:
switchD_005c061b_caseD_80070772:
      return (int)"ERROR_INVALID_PRINTER_STATE";
    case 0x773:
switchD_005c061b_caseD_80070773:
      return (int)"ERROR_PASSWORD_MUST_CHANGE";
    case 0x774:
switchD_005c061b_caseD_80070774:
      return (int)"ERROR_DOMAIN_CONTROLLER_NOT_FOUND";
    case 0x775:
switchD_005c061b_caseD_80070775:
      return (int)"ERROR_ACCOUNT_LOCKED_OUT";
    case 0x776:
switchD_005c061b_caseD_80070776:
      return (int)"OR_INVALID_OXID";
    case 0x777:
switchD_005c061b_caseD_80070777:
      return (int)"OR_INVALID_OID";
    case 0x778:
switchD_005c061b_caseD_80070778:
      return (int)"OR_INVALID_SET";
    case 0x779:
switchD_005c061b_caseD_80070779:
      return (int)"RPC_S_SEND_INCOMPLETE";
    case 0x77a:
switchD_005c061b_caseD_8007077a:
      return (int)"RPC_S_INVALID_ASYNC_HANDLE";
    case 0x77b:
switchD_005c061b_caseD_8007077b:
      return (int)"RPC_S_INVALID_ASYNC_CALL";
    case 0x77c:
      goto switchD_005c6079_caseD_77c;
    case 0x77d:
switchD_005c063f_caseD_8007077d:
      return (int)"RPC_X_PIPE_DISCIPLINE_ERROR";
    case 0x77e:
switchD_005c063f_caseD_8007077e:
      return (int)"RPC_X_PIPE_EMPTY";
    case 0x77f:
switchD_005c063f_caseD_8007077f:
      return (int)"ERROR_NO_SITENAME";
    case 0x780:
switchD_005c063f_caseD_80070780:
      return (int)"ERROR_CANT_ACCESS_FILE";
    case 0x781:
switchD_005c063f_caseD_80070781:
      return (int)"ERROR_CANT_RESOLVE_FILENAME";
    case 0x782:
switchD_005c063f_caseD_80070782:
      return (int)"RPC_S_ENTRY_TYPE_MISMATCH";
    case 0x783:
switchD_005c063f_caseD_80070783:
      return (int)"RPC_S_NOT_ALL_OBJS_EXPORTED";
    case 0x784:
switchD_005c063f_caseD_80070784:
      return (int)"RPC_S_INTERFACE_NOT_EXPORTED";
    case 0x785:
switchD_005c063f_caseD_80070785:
      return (int)"RPC_S_PROFILE_NOT_ADDED";
    case 0x786:
switchD_005c063f_caseD_80070786:
      return (int)"RPC_S_PRF_ELT_NOT_ADDED";
    case 0x787:
switchD_005c063f_caseD_80070787:
      return (int)"RPC_S_PRF_ELT_NOT_REMOVED";
    case 0x788:
switchD_005c063f_caseD_80070788:
      return (int)"RPC_S_GRP_ELT_NOT_ADDED";
    case 0x789:
switchD_005c063f_caseD_80070789:
      return (int)"RPC_S_GRP_ELT_NOT_REMOVED";
    case 0x78a:
switchD_005c063f_caseD_8007078a:
      return (int)"ERROR_KM_DRIVER_BLOCKED";
    case 0x78b:
switchD_005c063f_caseD_8007078b:
      return (int)"ERROR_CONTEXT_EXPIRED";
    case 0x78c:
switchD_005c063f_caseD_8007078c:
      return (int)"ERROR_PER_USER_TRUST_QUOTA_EXCEEDED";
    case 0x78d:
switchD_005c063f_caseD_8007078d:
      return (int)"ERROR_ALL_USER_TRUST_QUOTA_EXCEEDED";
    case 0x78e:
switchD_005c063f_caseD_8007078e:
      return (int)"ERROR_USER_DELETE_TRUST_QUOTA_EXCEEDED";
    case 2000:
      goto switchD_005c6079_caseD_7d0;
    case 0x7d1:
switchD_005c0663_caseD_800707d1:
      return (int)"ERROR_BAD_DRIVER";
    case 0x7d2:
switchD_005c0663_caseD_800707d2:
      return (int)"ERROR_INVALID_WINDOW_STYLE";
    case 0x7d3:
switchD_005c0663_caseD_800707d3:
      return (int)"ERROR_METAFILE_NOT_SUPPORTED";
    case 0x7d4:
switchD_005c0663_caseD_800707d4:
      return (int)"ERROR_TRANSFORM_NOT_SUPPORTED";
    case 0x7d5:
switchD_005c0663_caseD_800707d5:
      return (int)"ERROR_CLIPPING_NOT_SUPPORTED";
    case 0x7da:
switchD_005c0663_caseD_800707da:
      return (int)"ERROR_INVALID_CMM";
    case 0x7db:
switchD_005c0663_caseD_800707db:
      return (int)"ERROR_INVALID_PROFILE";
    case 0x7dc:
switchD_005c0663_caseD_800707dc:
      return (int)"ERROR_TAG_NOT_FOUND";
    case 0x7dd:
switchD_005c0663_caseD_800707dd:
      return (int)"ERROR_TAG_NOT_PRESENT";
    case 0x7de:
switchD_005c0663_caseD_800707de:
      return (int)"ERROR_DUPLICATE_TAG";
    case 0x7df:
switchD_005c0663_caseD_800707df:
      return (int)"ERROR_PROFILE_NOT_ASSOCIATED_WITH_DEVICE";
    case 0x7e0:
switchD_005c0663_caseD_800707e0:
      return (int)"ERROR_PROFILE_NOT_FOUND";
    case 0x7e1:
switchD_005c0663_caseD_800707e1:
      return (int)"ERROR_INVALID_COLORSPACE";
    case 0x7e2:
switchD_005c0663_caseD_800707e2:
      return (int)"ERROR_ICM_NOT_ENABLED";
    case 0x7e3:
switchD_005c0663_caseD_800707e3:
      return (int)"ERROR_DELETING_ICM_XFORM";
    case 0x7e4:
switchD_005c0663_caseD_800707e4:
      return (int)"ERROR_INVALID_TRANSFORM";
    case 0x7e5:
switchD_005c0663_caseD_800707e5:
      return (int)"ERROR_COLORSPACE_MISMATCH";
    case 0x7e6:
switchD_005c0663_caseD_800707e6:
      return (int)"ERROR_INVALID_COLORINDEX";
    case 0x83c:
switchD_005c6079_caseD_83c:
      return (int)"ERROR_CONNECTED_OTHER_PASSWORD";
    case 0x83d:
switchD_005c6079_caseD_83d:
      return (int)"ERROR_CONNECTED_OTHER_PASSWORD_DEFAULT";
    case 0x89a:
switchD_005c6079_caseD_89a:
      return (int)"ERROR_BAD_USERNAME";
    }
  }
  else if (in_stack_00000004 < 0x215e) {
    if (in_stack_00000004 == 0x215d) {
switchD_005c0b64_caseD_8007215d:
      return (int)"ERROR_SAM_INIT_FAILURE";
    }
    if (in_stack_00000004 < 0x2018) {
      if (in_stack_00000004 == 0x2017) {
switchD_005c0b4d_caseD_80072017:
        return (int)"ERROR_DS_CANT_MOD_OBJ_CLASS";
      }
      if (in_stack_00000004 < 0x13be) {
        if (in_stack_00000004 == 0x13bd) {
switchD_005c0990_caseD_800713bd:
          return (int)"ERROR_CLUSTER_JOIN_NOT_IN_PROGRESS";
        }
        if (in_stack_00000004 < 0x10eb) {
          if (in_stack_00000004 == 0x10ea) {
switchD_005c0835_caseD_800710ea:
            return (int)"ERROR_UNABLE_TO_EJECT_MOUNTED_MEDIA";
          }
          if (in_stack_00000004 < 0x1072) {
            if (in_stack_00000004 == 0x1071) {
switchD_005c0819_caseD_80071071:
              return (int)"ERROR_WMI_DP_FAILED";
            }
            if (in_stack_00000004 < 0xbc7) {
              if (in_stack_00000004 == 0xbc6) {
LAB_005c690b:
                return (int)"ERROR_PRINTER_DRIVER_BLOCKED";
              }
              if (in_stack_00000004 < 0xbbe) {
                if (in_stack_00000004 == 0xbbd) {
switchD_005c077f_caseD_80070bbd:
                  return (int)"ERROR_PRINT_PROCESSOR_ALREADY_INSTALLED";
                }
                if (in_stack_00000004 < 0xbba) {
                  if (in_stack_00000004 == 0xbb9) {
LAB_005c6869:
                    return (int)"ERROR_PRINTER_DRIVER_IN_USE";
                  }
                  if (in_stack_00000004 == 0x961) {
LAB_005c685f:
                    return (int)"ERROR_OPEN_FILES";
                  }
                  if (in_stack_00000004 == 0x962) {
LAB_005c0731:
                    return (int)"ERROR_ACTIVE_CONNECTIONS";
                  }
                  if (in_stack_00000004 == 0x964) goto LAB_005c6855;
                  if (in_stack_00000004 == 3000) goto LAB_005c684b;
                }
                else {
                  if (in_stack_00000004 == 0xbba) {
LAB_005c6892:
                    return (int)"ERROR_SPOOL_FILE_NOT_FOUND";
                  }
                  if (in_stack_00000004 == 0xbbb) {
LAB_005c0767:
                    return (int)"ERROR_SPL_NO_STARTDOC";
                  }
                  if (in_stack_00000004 == 0xbbc) goto LAB_005c6888;
                }
              }
              else {
                switch(in_stack_00000004) {
                case 0xbbe:
switchD_005c077f_caseD_80070bbe:
                  return (int)"ERROR_PRINT_MONITOR_ALREADY_INSTALLED";
                case 0xbbf:
switchD_005c077f_caseD_80070bbf:
                  return (int)"ERROR_INVALID_PRINT_MONITOR";
                case 0xbc0:
switchD_005c077f_caseD_80070bc0:
                  return (int)"ERROR_PRINT_MONITOR_IN_USE";
                case 0xbc1:
switchD_005c077f_caseD_80070bc1:
                  return (int)"ERROR_PRINTER_HAS_JOBS_QUEUED";
                case 0xbc2:
switchD_005c077f_caseD_80070bc2:
                  return (int)"ERROR_SUCCESS_REBOOT_REQUIRED";
                case 0xbc3:
switchD_005c077f_caseD_80070bc3:
                  return (int)"ERROR_SUCCESS_RESTART_REQUIRED";
                case 0xbc4:
switchD_005c077f_caseD_80070bc4:
                  return (int)"ERROR_PRINTER_NOT_FOUND";
                case 0xbc5:
switchD_005c077f_caseD_80070bc5:
                  return (int)"ERROR_PRINTER_DRIVER_WARNED";
                }
              }
            }
            else if (in_stack_00000004 < 0x1069) {
              if (in_stack_00000004 == 0x1068) {
LAB_005c0801:
                return (int)"ERROR_WMI_GUID_NOT_FOUND";
              }
              if (in_stack_00000004 < 0xfa5) {
                if (in_stack_00000004 == 0xfa4) {
LAB_005c696f:
                  return (int)"ERROR_FULL_BACKUP";
                }
                if (in_stack_00000004 == 4000) {
LAB_005c6965:
                  return (int)"ERROR_WINS_INTERNAL";
                }
                if (in_stack_00000004 == 0xfa1) {
LAB_005c695b:
                  return (int)"ERROR_CAN_NOT_DEL_LOCAL_WINS";
                }
                if (in_stack_00000004 == 0xfa2) {
LAB_005c6951:
                  return (int)"ERROR_STATIC_INIT";
                }
                if (in_stack_00000004 == 0xfa3) {
LAB_005c6947:
                  return (int)"ERROR_INC_BACKUP";
                }
              }
              else {
                if (in_stack_00000004 == 0xfa5) {
LAB_005c69a0:
                  return (int)"ERROR_REC_NON_EXISTENT";
                }
                if (in_stack_00000004 == 0xfa6) {
LAB_005c6996:
                  return (int)"ERROR_RPL_NOT_ALLOWED";
                }
                if (in_stack_00000004 == 0x1004) {
LAB_005c698c:
                  return (int)"ERROR_DHCP_ADDRESS_CONFLICT";
                }
              }
            }
            else {
              switch(in_stack_00000004) {
              case 0x1069:
switchD_005c69b8_caseD_1069:
                return (int)"ERROR_WMI_INSTANCE_NOT_FOUND";
              case 0x106a:
switchD_005c0819_caseD_8007106a:
                return (int)"ERROR_WMI_ITEMID_NOT_FOUND";
              case 0x106b:
switchD_005c0819_caseD_8007106b:
                return (int)"ERROR_WMI_TRY_AGAIN";
              case 0x106c:
switchD_005c0819_caseD_8007106c:
                return (int)"ERROR_WMI_DP_NOT_FOUND";
              case 0x106d:
switchD_005c0819_caseD_8007106d:
                return (int)"ERROR_WMI_UNRESOLVED_INSTANCE_REF";
              case 0x106e:
switchD_005c0819_caseD_8007106e:
                return (int)"ERROR_WMI_ALREADY_ENABLED";
              case 0x106f:
switchD_005c0819_caseD_8007106f:
                return (int)"ERROR_WMI_GUID_DISCONNECTED";
              case 0x1070:
switchD_005c0819_caseD_80071070:
                return (int)"ERROR_WMI_SERVER_UNAVAILABLE";
              }
            }
          }
          else {
            switch(in_stack_00000004) {
            case 0x1072:
switchD_005c0819_caseD_80071072:
              return (int)"ERROR_WMI_INVALID_MOF";
            case 0x1073:
switchD_005c6a2e_caseD_1073:
              return (int)"ERROR_WMI_INVALID_REGINFO";
            case 0x1074:
switchD_005c0835_caseD_80071074:
              return (int)"ERROR_WMI_ALREADY_DISABLED";
            case 0x1075:
switchD_005c0835_caseD_80071075:
              return (int)"ERROR_WMI_READ_ONLY";
            case 0x1076:
switchD_005c0835_caseD_80071076:
              return (int)"ERROR_WMI_SET_FAILURE";
            case 0x10cc:
switchD_005c0835_caseD_800710cc:
              return (int)"ERROR_INVALID_MEDIA";
            case 0x10cd:
switchD_005c0835_caseD_800710cd:
              return (int)"ERROR_INVALID_LIBRARY";
            case 0x10ce:
switchD_005c0835_caseD_800710ce:
              return (int)"ERROR_INVALID_MEDIA_POOL";
            case 0x10cf:
switchD_005c0835_caseD_800710cf:
              return (int)"ERROR_DRIVE_MEDIA_MISMATCH";
            case 0x10d0:
switchD_005c0835_caseD_800710d0:
              return (int)"ERROR_MEDIA_OFFLINE";
            case 0x10d1:
switchD_005c0835_caseD_800710d1:
              return (int)"ERROR_LIBRARY_OFFLINE";
            case 0x10d2:
switchD_005c0835_caseD_800710d2:
              return (int)"ERROR_EMPTY";
            case 0x10d3:
switchD_005c0835_caseD_800710d3:
              return (int)"ERROR_NOT_EMPTY";
            case 0x10d4:
switchD_005c0835_caseD_800710d4:
              return (int)"ERROR_MEDIA_UNAVAILABLE";
            case 0x10d5:
switchD_005c0835_caseD_800710d5:
              return (int)"ERROR_RESOURCE_DISABLED";
            case 0x10d6:
switchD_005c0835_caseD_800710d6:
              return (int)"ERROR_INVALID_CLEANER";
            case 0x10d7:
switchD_005c0835_caseD_800710d7:
              return (int)"ERROR_UNABLE_TO_CLEAN";
            case 0x10d8:
switchD_005c0835_caseD_800710d8:
              return (int)"ERROR_OBJECT_NOT_FOUND";
            case 0x10d9:
switchD_005c0835_caseD_800710d9:
              return (int)"ERROR_DATABASE_FAILURE";
            case 0x10da:
switchD_005c0835_caseD_800710da:
              return (int)"ERROR_DATABASE_FULL";
            case 0x10db:
switchD_005c0835_caseD_800710db:
              return (int)"ERROR_MEDIA_INCOMPATIBLE";
            case 0x10dc:
switchD_005c0835_caseD_800710dc:
              return (int)"ERROR_RESOURCE_NOT_PRESENT";
            case 0x10dd:
switchD_005c0835_caseD_800710dd:
              return (int)"ERROR_INVALID_OPERATION";
            case 0x10de:
switchD_005c0835_caseD_800710de:
              return (int)"ERROR_MEDIA_NOT_AVAILABLE";
            case 0x10df:
switchD_005c0835_caseD_800710df:
              return (int)"ERROR_DEVICE_NOT_AVAILABLE";
            case 0x10e0:
switchD_005c0835_caseD_800710e0:
              return (int)"ERROR_REQUEST_REFUSED";
            case 0x10e1:
switchD_005c0835_caseD_800710e1:
              return (int)"ERROR_INVALID_DRIVE_OBJECT";
            case 0x10e2:
switchD_005c0835_caseD_800710e2:
              return (int)"ERROR_LIBRARY_FULL";
            case 0x10e3:
switchD_005c0835_caseD_800710e3:
              return (int)"ERROR_MEDIUM_NOT_ACCESSIBLE";
            case 0x10e4:
switchD_005c0835_caseD_800710e4:
              return (int)"ERROR_UNABLE_TO_LOAD_MEDIUM";
            case 0x10e5:
switchD_005c0835_caseD_800710e5:
              return (int)"ERROR_UNABLE_TO_INVENTORY_DRIVE";
            case 0x10e6:
switchD_005c0835_caseD_800710e6:
              return (int)"ERROR_UNABLE_TO_INVENTORY_SLOT";
            case 0x10e7:
switchD_005c0835_caseD_800710e7:
              return (int)"ERROR_UNABLE_TO_INVENTORY_TRANSPORT";
            case 0x10e8:
switchD_005c0835_caseD_800710e8:
              return (int)"ERROR_TRANSPORT_FULL";
            case 0x10e9:
switchD_005c0835_caseD_800710e9:
              return (int)"ERROR_CONTROLLING_IEPORT";
            }
          }
        }
        else if (in_stack_00000004 < 0x1127) {
          if (in_stack_00000004 == 0x1126) {
LAB_005c6c44:
            return (int)"ERROR_NOT_A_REPARSE_POINT";
          }
          switch(in_stack_00000004) {
          case 0x10eb:
switchD_005c0835_caseD_800710eb:
            return (int)"ERROR_CLEANER_SLOT_SET";
          case 0x10ec:
switchD_005c0835_caseD_800710ec:
            return (int)"ERROR_CLEANER_SLOT_NOT_SET";
          case 0x10ed:
switchD_005c0835_caseD_800710ed:
            return (int)"ERROR_CLEANER_CARTRIDGE_SPENT";
          case 0x10ee:
switchD_005c0835_caseD_800710ee:
            return (int)"ERROR_UNEXPECTED_OMID";
          case 0x10ef:
switchD_005c0835_caseD_800710ef:
            return (int)"ERROR_CANT_DELETE_LAST_ITEM";
          case 0x10f0:
            goto switchD_005c6bc5_caseD_10f0;
          case 0x10f1:
switchD_005c6bc5_caseD_10f1:
            return (int)"ERROR_VOLUME_CONTAINS_SYS_FILES";
          case 0x10f2:
switchD_005c6bc5_caseD_10f2:
            return (int)"ERROR_INDIGENOUS_TYPE";
          case 0x10f3:
switchD_005c6bc5_caseD_10f3:
            return (int)"ERROR_NO_SUPPORTING_DRIVES";
          case 0x10f4:
switchD_005c6bc5_caseD_10f4:
            return (int)"ERROR_CLEANER_CARTRIDGE_INSTALLED";
          case 0x10fe:
switchD_005c6bc5_caseD_10fe:
            return (int)"ERROR_FILE_OFFLINE";
          case 0x10ff:
switchD_005c6bc5_caseD_10ff:
            return (int)"ERROR_REMOTE_STORAGE_NOT_ACTIVE";
          case 0x1100:
switchD_005c6bc5_caseD_1100:
            return (int)"ERROR_REMOTE_STORAGE_MEDIA_ERROR";
          }
        }
        else if (in_stack_00000004 < 0x13a1) {
          if (in_stack_00000004 == 0x13a0) {
switchD_005c097b_caseD_800713a0:
            return (int)"ERROR_RESOURCE_PROPERTIES_STORED";
          }
          if (in_stack_00000004 < 0x1393) {
            if (in_stack_00000004 == 0x1392) {
switchD_005c097b_caseD_80071392:
              return (int)"ERROR_OBJECT_ALREADY_EXISTS";
            }
            if (in_stack_00000004 < 0x138c) {
              if (in_stack_00000004 == 0x138b) {
LAB_005c6ce0:
                return (int)"ERROR_DEPENDENCY_ALREADY_EXISTS";
              }
              if (in_stack_00000004 == 0x1127) {
LAB_005c6cd6:
                return (int)"ERROR_REPARSE_ATTRIBUTE_CONFLICT";
              }
              if (in_stack_00000004 == 0x1128) {
LAB_005c08ed:
                return (int)"ERROR_INVALID_REPARSE_DATA";
              }
              if (in_stack_00000004 == 0x1129) goto LAB_005c6ccc;
              if (in_stack_00000004 == 0x112a) goto LAB_005c6cc2;
              if (in_stack_00000004 == 0x1194) goto LAB_005c6cb8;
              if (in_stack_00000004 == 0x1389) goto LAB_005c6cae;
              if (in_stack_00000004 == 0x138a) goto LAB_005c6ca4;
            }
            else {
              if (in_stack_00000004 == 0x138c) {
LAB_005c6d30:
                return (int)"ERROR_RESOURCE_NOT_ONLINE";
              }
              if (in_stack_00000004 == 0x138d) {
LAB_005c6d26:
                return (int)"ERROR_HOST_NODE_NOT_AVAILABLE";
              }
              if (in_stack_00000004 == 0x138e) {
LAB_005c6d1c:
                return (int)"ERROR_RESOURCE_NOT_AVAILABLE";
              }
              if (in_stack_00000004 == 0x138f) {
LAB_005c0963:
                return (int)"ERROR_RESOURCE_NOT_FOUND";
              }
              if (in_stack_00000004 == 0x1390) goto LAB_005c6d12;
              if (in_stack_00000004 == 0x1391) goto switchD_005c097b_caseD_80071391;
            }
          }
          else {
            switch(in_stack_00000004) {
            case 0x1393:
switchD_005c097b_caseD_80071393:
              return (int)"ERROR_OBJECT_IN_LIST";
            case 0x1394:
switchD_005c097b_caseD_80071394:
              return (int)"ERROR_GROUP_NOT_AVAILABLE";
            case 0x1395:
switchD_005c097b_caseD_80071395:
              return (int)"ERROR_GROUP_NOT_FOUND";
            case 0x1396:
switchD_005c097b_caseD_80071396:
              return (int)"ERROR_GROUP_NOT_ONLINE";
            case 0x1397:
switchD_005c097b_caseD_80071397:
              return (int)"ERROR_HOST_NODE_NOT_RESOURCE_OWNER";
            case 0x1398:
switchD_005c097b_caseD_80071398:
              return (int)"ERROR_HOST_NODE_NOT_GROUP_OWNER";
            case 0x1399:
switchD_005c097b_caseD_80071399:
              return (int)"ERROR_RESMON_CREATE_FAILED";
            case 0x139a:
switchD_005c097b_caseD_8007139a:
              return (int)"ERROR_RESMON_ONLINE_FAILED";
            case 0x139b:
switchD_005c097b_caseD_8007139b:
              return (int)"ERROR_RESOURCE_ONLINE";
            case 0x139c:
switchD_005c097b_caseD_8007139c:
              return (int)"ERROR_QUORUM_RESOURCE";
            case 0x139d:
switchD_005c097b_caseD_8007139d:
              return (int)"ERROR_NOT_QUORUM_CAPABLE";
            case 0x139e:
switchD_005c097b_caseD_8007139e:
              return (int)"ERROR_CLUSTER_SHUTTING_DOWN";
            case 0x139f:
switchD_005c097b_caseD_8007139f:
              return (int)"ERROR_INVALID_STATE";
            }
          }
        }
        else {
          switch(in_stack_00000004) {
          case 0x13a1:
switchD_005c097b_caseD_800713a1:
            return (int)"ERROR_NOT_QUORUM_CLASS";
          case 0x13a2:
switchD_005c097b_caseD_800713a2:
            return (int)"ERROR_CORE_RESOURCE";
          case 0x13a3:
switchD_005c097b_caseD_800713a3:
            return (int)"ERROR_QUORUM_RESOURCE_ONLINE_FAILED";
          case 0x13a4:
switchD_005c6df3_caseD_13a4:
            return (int)"ERROR_QUORUMLOG_OPEN_FAILED";
          case 0x13a5:
switchD_005c0990_caseD_800713a5:
            return (int)"ERROR_CLUSTERLOG_CORRUPT";
          case 0x13a6:
switchD_005c0990_caseD_800713a6:
            return (int)"ERROR_CLUSTERLOG_RECORD_EXCEEDS_MAXSIZE";
          case 0x13a7:
switchD_005c0990_caseD_800713a7:
            return (int)"ERROR_CLUSTERLOG_EXCEEDS_MAXSIZE";
          case 0x13a8:
switchD_005c0990_caseD_800713a8:
            return (int)"ERROR_CLUSTERLOG_CHKPOINT_NOT_FOUND";
          case 0x13a9:
switchD_005c0990_caseD_800713a9:
            return (int)"ERROR_CLUSTERLOG_NOT_ENOUGH_SPACE";
          case 0x13aa:
switchD_005c0990_caseD_800713aa:
            return (int)"ERROR_QUORUM_OWNER_ALIVE";
          case 0x13ab:
switchD_005c0990_caseD_800713ab:
            return (int)"ERROR_NETWORK_NOT_AVAILABLE";
          case 0x13ac:
switchD_005c0990_caseD_800713ac:
            return (int)"ERROR_NODE_NOT_AVAILABLE";
          case 0x13ad:
switchD_005c0990_caseD_800713ad:
            return (int)"ERROR_ALL_NODES_NOT_AVAILABLE";
          case 0x13ae:
switchD_005c0990_caseD_800713ae:
            return (int)"ERROR_RESOURCE_FAILED";
          case 0x13af:
switchD_005c0990_caseD_800713af:
            return (int)"ERROR_CLUSTER_INVALID_NODE";
          case 0x13b0:
switchD_005c0990_caseD_800713b0:
            return (int)"ERROR_CLUSTER_NODE_EXISTS";
          case 0x13b1:
switchD_005c0990_caseD_800713b1:
            return (int)"ERROR_CLUSTER_JOIN_IN_PROGRESS";
          case 0x13b2:
switchD_005c0990_caseD_800713b2:
            return (int)"ERROR_CLUSTER_NODE_NOT_FOUND";
          case 0x13b3:
switchD_005c0990_caseD_800713b3:
            return (int)"ERROR_CLUSTER_LOCAL_NODE_NOT_FOUND";
          case 0x13b4:
switchD_005c0990_caseD_800713b4:
            return (int)"ERROR_CLUSTER_NETWORK_EXISTS";
          case 0x13b5:
switchD_005c0990_caseD_800713b5:
            return (int)"ERROR_CLUSTER_NETWORK_NOT_FOUND";
          case 0x13b6:
switchD_005c0990_caseD_800713b6:
            return (int)"ERROR_CLUSTER_NETINTERFACE_EXISTS";
          case 0x13b7:
switchD_005c0990_caseD_800713b7:
            return (int)"ERROR_CLUSTER_NETINTERFACE_NOT_FOUND";
          case 0x13b8:
switchD_005c0990_caseD_800713b8:
            return (int)"ERROR_CLUSTER_INVALID_REQUEST";
          case 0x13b9:
switchD_005c0990_caseD_800713b9:
            return (int)"ERROR_CLUSTER_INVALID_NETWORK_PROVIDER";
          case 0x13ba:
switchD_005c0990_caseD_800713ba:
            return (int)"ERROR_CLUSTER_NODE_DOWN";
          case 0x13bb:
switchD_005c0990_caseD_800713bb:
            return (int)"ERROR_CLUSTER_NODE_UNREACHABLE";
          case 0x13bc:
switchD_005c0990_caseD_800713bc:
            return (int)"ERROR_CLUSTER_NODE_NOT_MEMBER";
          }
        }
      }
      else if (in_stack_00000004 < 0x1703) {
        if (in_stack_00000004 == 0x1702) {
LAB_005c70a2:
          return (int)"ERROR_CLUSTER_MEMBERSHIP_INVALID_STATE";
        }
        switch(in_stack_00000004) {
        case 0x13be:
switchD_005c0990_caseD_800713be:
          return (int)"ERROR_CLUSTER_INVALID_NETWORK";
        case 0x13c0:
switchD_005c0990_caseD_800713c0:
          return (int)"ERROR_CLUSTER_NODE_UP";
        case 0x13c1:
switchD_005c0990_caseD_800713c1:
          return (int)"ERROR_CLUSTER_IPADDR_IN_USE";
        case 0x13c2:
switchD_005c0990_caseD_800713c2:
          return (int)"ERROR_CLUSTER_NODE_NOT_PAUSED";
        case 0x13c3:
switchD_005c0990_caseD_800713c3:
          return (int)"ERROR_CLUSTER_NO_SECURITY_CONTEXT";
        case 0x13c4:
switchD_005c0990_caseD_800713c4:
          return (int)"ERROR_CLUSTER_NETWORK_NOT_INTERNAL";
        case 0x13c5:
switchD_005c0990_caseD_800713c5:
          return (int)"ERROR_CLUSTER_NODE_ALREADY_UP";
        case 0x13c6:
switchD_005c0990_caseD_800713c6:
          return (int)"ERROR_CLUSTER_NODE_ALREADY_DOWN";
        case 0x13c7:
switchD_005c0990_caseD_800713c7:
          return (int)"ERROR_CLUSTER_NETWORK_ALREADY_ONLINE";
        case 0x13c8:
switchD_005c0990_caseD_800713c8:
          return (int)"ERROR_CLUSTER_NETWORK_ALREADY_OFFLINE";
        case 0x13c9:
switchD_005c0990_caseD_800713c9:
          return (int)"ERROR_CLUSTER_NODE_ALREADY_MEMBER";
        case 0x13ca:
switchD_005c0990_caseD_800713ca:
          return (int)"ERROR_CLUSTER_LAST_INTERNAL_NETWORK";
        case 0x13cb:
switchD_005c0990_caseD_800713cb:
          return (int)"ERROR_CLUSTER_NETWORK_HAS_DEPENDENTS";
        case 0x13cc:
switchD_005c0990_caseD_800713cc:
          return (int)"ERROR_INVALID_OPERATION_ON_QUORUM";
        case 0x13cd:
          goto switchD_005c6f3d_caseD_13cd;
        case 0x13ce:
switchD_005c09b4_caseD_800713ce:
          return (int)"ERROR_CLUSTER_NODE_PAUSED";
        case 0x13cf:
switchD_005c09b4_caseD_800713cf:
          return (int)"ERROR_NODE_CANT_HOST_RESOURCE";
        case 0x13d0:
switchD_005c09b4_caseD_800713d0:
          return (int)"ERROR_CLUSTER_NODE_NOT_READY";
        case 0x13d1:
switchD_005c09b4_caseD_800713d1:
          return (int)"ERROR_CLUSTER_NODE_SHUTTING_DOWN";
        case 0x13d2:
switchD_005c09b4_caseD_800713d2:
          return (int)"ERROR_CLUSTER_JOIN_ABORTED";
        case 0x13d3:
switchD_005c09b4_caseD_800713d3:
          return (int)"ERROR_CLUSTER_INCOMPATIBLE_VERSIONS";
        case 0x13d4:
switchD_005c09b4_caseD_800713d4:
          return (int)"ERROR_CLUSTER_MAXNUM_OF_RESOURCES_EXCEEDED";
        case 0x13d5:
switchD_005c09b4_caseD_800713d5:
          return (int)"ERROR_CLUSTER_SYSTEM_CONFIG_CHANGED";
        case 0x13d6:
switchD_005c09b4_caseD_800713d6:
          return (int)"ERROR_CLUSTER_RESOURCE_TYPE_NOT_FOUND";
        case 0x13d7:
switchD_005c09b4_caseD_800713d7:
          return (int)"ERROR_CLUSTER_RESTYPE_NOT_SUPPORTED";
        case 0x13d8:
switchD_005c09b4_caseD_800713d8:
          return (int)"ERROR_CLUSTER_RESNAME_NOT_FOUND";
        case 0x13d9:
switchD_005c09b4_caseD_800713d9:
          return (int)"ERROR_CLUSTER_NO_RPC_PACKAGES_REGISTERED";
        case 0x13da:
switchD_005c09b4_caseD_800713da:
          return (int)"ERROR_CLUSTER_OWNER_NOT_IN_PREFLIST";
        case 0x13db:
switchD_005c09b4_caseD_800713db:
          return (int)"ERROR_CLUSTER_DATABASE_SEQMISMATCH";
        case 0x13dc:
switchD_005c09b4_caseD_800713dc:
          return (int)"ERROR_RESMON_INVALID_STATE";
        case 0x13dd:
switchD_005c09b4_caseD_800713dd:
          return (int)"ERROR_CLUSTER_GUM_NOT_LOCKER";
        case 0x13de:
switchD_005c09b4_caseD_800713de:
          return (int)"ERROR_QUORUM_DISK_NOT_FOUND";
        case 0x13df:
switchD_005c09b4_caseD_800713df:
          return (int)"ERROR_DATABASE_BACKUP_CORRUPT";
        case 0x13e0:
switchD_005c09b4_caseD_800713e0:
          return (int)"ERROR_CLUSTER_NODE_ALREADY_HAS_DFS_ROOT";
        case 0x13e1:
switchD_005c09b4_caseD_800713e1:
          return (int)"ERROR_RESOURCE_PROPERTY_UNCHANGEABLE";
        }
      }
      else if (in_stack_00000004 < 0x1771) {
        if (in_stack_00000004 == 6000) {
LAB_005c716a:
          return (int)"ERROR_ENCRYPTION_FAILED";
        }
        switch(in_stack_00000004) {
        case 0x1703:
switchD_005c09d8_caseD_80071703:
          return (int)"ERROR_CLUSTER_QUORUMLOG_NOT_FOUND";
        case 0x1704:
switchD_005c09d8_caseD_80071704:
          return (int)"ERROR_CLUSTER_MEMBERSHIP_HALT";
        case 0x1705:
switchD_005c09d8_caseD_80071705:
          return (int)"ERROR_CLUSTER_INSTANCE_ID_MISMATCH";
        case 0x1706:
switchD_005c09d8_caseD_80071706:
          return (int)"ERROR_CLUSTER_NETWORK_NOT_FOUND_FOR_IP";
        case 0x1707:
switchD_005c09d8_caseD_80071707:
          return (int)"ERROR_CLUSTER_PROPERTY_DATA_TYPE_MISMATCH";
        case 0x1708:
switchD_005c09d8_caseD_80071708:
          return (int)"ERROR_CLUSTER_EVICT_WITHOUT_CLEANUP";
        case 0x1709:
switchD_005c09d8_caseD_80071709:
          return (int)"ERROR_CLUSTER_PARAMETER_MISMATCH";
        case 0x170a:
switchD_005c09d8_caseD_8007170a:
          return (int)"ERROR_NODE_CANNOT_BE_CLUSTERED";
        case 0x170b:
switchD_005c09d8_caseD_8007170b:
          return (int)"ERROR_CLUSTER_WRONG_OS_VERSION";
        case 0x170c:
switchD_005c09d8_caseD_8007170c:
          return (int)"ERROR_CLUSTER_CANT_CREATE_DUP_CLUSTER_NAME";
        case 0x170d:
switchD_005c09d8_caseD_8007170d:
          return (int)"ERROR_CLUSCFG_ALREADY_COMMITTED";
        case 0x170e:
switchD_005c09d8_caseD_8007170e:
          return (int)"ERROR_CLUSCFG_ROLLBACK_FAILED";
        case 0x170f:
switchD_005c09d8_caseD_8007170f:
          return (int)"ERROR_CLUSCFG_SYSTEM_DISK_DRIVE_LETTER_CONFLICT";
        case 0x1710:
switchD_005c09d8_caseD_80071710:
          return (int)"ERROR_CLUSTER_OLD_VERSION";
        case 0x1711:
switchD_005c09d8_caseD_80071711:
          return (int)"ERROR_CLUSTER_MISMATCHED_COMPUTER_ACCT_NAME";
        }
      }
      else if (in_stack_00000004 < 0x17e7) {
        if (in_stack_00000004 == 0x17e6) {
LAB_005c723c:
          return (int)"ERROR_NO_BROWSER_SERVERS_FOUND";
        }
        switch(in_stack_00000004) {
        case 0x1771:
switchD_005c09fc_caseD_80071771:
          return (int)"ERROR_DECRYPTION_FAILED";
        case 0x1772:
switchD_005c09fc_caseD_80071772:
          return (int)"ERROR_FILE_ENCRYPTED";
        case 0x1773:
switchD_005c09fc_caseD_80071773:
          return (int)"ERROR_NO_RECOVERY_POLICY";
        case 0x1774:
switchD_005c09fc_caseD_80071774:
          return (int)"ERROR_NO_EFS";
        case 0x1775:
switchD_005c09fc_caseD_80071775:
          return (int)"ERROR_WRONG_EFS";
        case 0x1776:
switchD_005c09fc_caseD_80071776:
          return (int)"ERROR_NO_USER_KEYS";
        case 0x1777:
switchD_005c09fc_caseD_80071777:
          return (int)"ERROR_FILE_NOT_ENCRYPTED";
        case 0x1778:
switchD_005c09fc_caseD_80071778:
          return (int)"ERROR_NOT_EXPORT_FORMAT";
        case 0x1779:
switchD_005c09fc_caseD_80071779:
          return (int)"ERROR_FILE_READ_ONLY";
        case 0x177a:
switchD_005c09fc_caseD_8007177a:
          return (int)"ERROR_DIR_EFS_DISALLOWED";
        case 0x177b:
switchD_005c09fc_caseD_8007177b:
          return (int)"ERROR_EFS_SERVER_NOT_TRUSTED";
        case 0x177c:
switchD_005c09fc_caseD_8007177c:
          return (int)"ERROR_BAD_RECOVERY_POLICY";
        case 0x177d:
switchD_005c09fc_caseD_8007177d:
          return (int)"ERROR_EFS_ALG_BLOB_TOO_BIG";
        case 0x177e:
switchD_005c09fc_caseD_8007177e:
          return (int)"ERROR_VOLUME_NOT_SUPPORT_EFS";
        case 0x177f:
switchD_005c09fc_caseD_8007177f:
          return (int)"ERROR_EFS_DISABLED";
        case 0x1780:
switchD_005c09fc_caseD_80071780:
          return (int)"ERROR_EFS_VERSION_NOT_SUPPORT";
        }
      }
      else if (in_stack_00000004 < 0x1b90) {
        if (in_stack_00000004 == 0x1b8f) {
switchD_005c0b1a_caseD_80071b8f:
          return (int)"ERROR_CTX_LICENSE_CLIENT_INVALID";
        }
        if (in_stack_00000004 < 0x1b6f) {
          if (in_stack_00000004 == 0x1b6e) {
switchD_005c0af6_caseD_80071b6e:
            return (int)"ERROR_CTX_WINSTATION_NOT_FOUND";
          }
          if (in_stack_00000004 < 0x1b62) {
            if (in_stack_00000004 == 0x1b61) {
LAB_005c7306:
              return (int)"ERROR_CTX_MODEM_INF_NOT_FOUND";
            }
            if (in_stack_00000004 < 0x1b5d) {
              if (in_stack_00000004 == 0x1b5c) {
LAB_005c72c6:
                return (int)"ERROR_CTX_WD_NOT_FOUND";
              }
              if (in_stack_00000004 == 0x1838) {
LAB_005c72bc:
                return (int)"SCHED_E_SERVICE_NOT_LOCALSYSTEM";
              }
              if (in_stack_00000004 == 0x1b59) {
LAB_005c72b2:
                return (int)"ERROR_CTX_WINSTATION_NAME_INVALID";
              }
              if (in_stack_00000004 == 0x1b5a) {
LAB_005c72a8:
                return (int)"ERROR_CTX_INVALID_PD";
              }
              if (in_stack_00000004 == 0x1b5b) {
LAB_005c729e:
                return (int)"ERROR_CTX_PD_NOT_FOUND";
              }
            }
            else {
              if (in_stack_00000004 == 0x1b5d) {
LAB_005c0a8b:
                return (int)"ERROR_CTX_CANNOT_MAKE_EVENTLOG_ENTRY";
              }
              if (in_stack_00000004 == 0x1b5e) {
LAB_005c72fc:
                return (int)"ERROR_CTX_SERVICE_NAME_COLLISION";
              }
              if (in_stack_00000004 == 0x1b5f) goto LAB_005c72f2;
              if (in_stack_00000004 == 0x1b60) goto LAB_005c72e8;
            }
          }
          else {
            switch(in_stack_00000004) {
            case 0x1b62:
switchD_005c731e_caseD_1b62:
              return (int)"ERROR_CTX_INVALID_MODEMNAME";
            case 0x1b63:
switchD_005c731e_caseD_1b63:
              return (int)"ERROR_CTX_MODEM_RESPONSE_ERROR";
            case 0x1b64:
switchD_005c731e_caseD_1b64:
              return (int)"ERROR_CTX_MODEM_RESPONSE_TIMEOUT";
            case 0x1b65:
switchD_005c731e_caseD_1b65:
              return (int)"ERROR_CTX_MODEM_RESPONSE_NO_CARRIER";
            case 0x1b66:
switchD_005c0af6_caseD_80071b66:
              return (int)"ERROR_CTX_MODEM_RESPONSE_NO_DIALTONE";
            case 0x1b67:
switchD_005c0af6_caseD_80071b67:
              return (int)"ERROR_CTX_MODEM_RESPONSE_BUSY";
            case 0x1b68:
switchD_005c0af6_caseD_80071b68:
              return (int)"ERROR_CTX_MODEM_RESPONSE_VOICE";
            case 0x1b69:
switchD_005c0af6_caseD_80071b69:
              return (int)"ERROR_CTX_TD_ERROR";
            }
          }
        }
        else {
          switch(in_stack_00000004) {
          case 0x1b6f:
switchD_005c0af6_caseD_80071b6f:
            return (int)"ERROR_CTX_WINSTATION_ALREADY_EXISTS";
          case 0x1b70:
switchD_005c0af6_caseD_80071b70:
            return (int)"ERROR_CTX_WINSTATION_BUSY";
          case 0x1b71:
switchD_005c0af6_caseD_80071b71:
            return (int)"ERROR_CTX_BAD_VIDEO_MODE";
          case 0x1b7b:
switchD_005c0af6_caseD_80071b7b:
            return (int)"ERROR_CTX_GRAPHICS_INVALID";
          case 0x1b7d:
switchD_005c0af6_caseD_80071b7d:
            return (int)"ERROR_CTX_LOGON_DISABLED";
          case 0x1b7e:
switchD_005c0af6_caseD_80071b7e:
            return (int)"ERROR_CTX_NOT_CONSOLE";
          case 0x1b80:
switchD_005c0af6_caseD_80071b80:
            return (int)"ERROR_CTX_CLIENT_QUERY_TIMEOUT";
          case 0x1b81:
switchD_005c738a_caseD_1b81:
            return (int)"ERROR_CTX_CONSOLE_DISCONNECT";
          case 0x1b82:
switchD_005c0b1a_caseD_80071b82:
            return (int)"ERROR_CTX_CONSOLE_CONNECT";
          case 0x1b84:
switchD_005c0b1a_caseD_80071b84:
            return (int)"ERROR_CTX_SHADOW_DENIED";
          case 0x1b85:
switchD_005c0b1a_caseD_80071b85:
            return (int)"ERROR_CTX_WINSTATION_ACCESS_DENIED";
          case 0x1b89:
switchD_005c0b1a_caseD_80071b89:
            return (int)"ERROR_CTX_INVALID_WD";
          case 0x1b8a:
switchD_005c0b1a_caseD_80071b8a:
            return (int)"ERROR_CTX_SHADOW_INVALID";
          case 0x1b8b:
switchD_005c0b1a_caseD_80071b8b:
            return (int)"ERROR_CTX_SHADOW_DISABLED";
          case 0x1b8c:
switchD_005c0b1a_caseD_80071b8c:
            return (int)"ERROR_CTX_CLIENT_LICENSE_IN_USE";
          case 0x1b8d:
switchD_005c0b1a_caseD_80071b8d:
            return (int)"ERROR_CTX_CLIENT_LICENSE_NOT_SET";
          case 0x1b8e:
switchD_005c0b1a_caseD_80071b8e:
            return (int)"ERROR_CTX_LICENSE_NOT_AVAILABLE";
          }
        }
      }
      else if (in_stack_00000004 < 0x1f50) {
        if (in_stack_00000004 == 0x1f4f) {
switchD_005c0b4d_caseD_80071f4f:
          return (int)"FRS_ERR_SYSVOL_IS_BUSY";
        }
        if (in_stack_00000004 < 0x1f47) {
          if (in_stack_00000004 == 0x1f46) {
switchD_005c0b2f_caseD_80071f46:
            return (int)"FRS_ERR_SERVICE_COMM";
          }
          if (in_stack_00000004 < 0x1f42) {
            if (in_stack_00000004 == 0x1f41) goto LAB_005c74b0;
            if (in_stack_00000004 == 0x1b90) goto switchD_005c0b1a_caseD_80071b90;
            if (in_stack_00000004 == 0x1b91) goto switchD_005c0b1a_caseD_80071b91;
            if (in_stack_00000004 == 0x1b92) goto switchD_005c0b1a_caseD_80071b92;
            if (in_stack_00000004 == 0x1b93) goto switchD_005c0b1a_caseD_80071b93;
          }
          else {
            if (in_stack_00000004 == 0x1f42) goto switchD_005c0b2f_caseD_80071f42;
            if (in_stack_00000004 == 0x1f43) goto switchD_005c0b2f_caseD_80071f43;
            if (in_stack_00000004 == 0x1f44) goto switchD_005c0b2f_caseD_80071f44;
            if (in_stack_00000004 == 0x1f45) goto switchD_005c0b2f_caseD_80071f45;
          }
        }
        else {
          switch(in_stack_00000004) {
          case 0x1f47:
switchD_005c0b2f_caseD_80071f47:
            return (int)"FRS_ERR_INSUFFICIENT_PRIV";
          case 0x1f48:
switchD_005c0b2f_caseD_80071f48:
            return (int)"FRS_ERR_AUTHENTICATION";
          case 0x1f49:
switchD_005c0b2f_caseD_80071f49:
            return (int)"FRS_ERR_PARENT_INSUFFICIENT_PRIV";
          case 0x1f4a:
switchD_005c0b2f_caseD_80071f4a:
            return (int)"FRS_ERR_PARENT_AUTHENTICATION";
          case 0x1f4b:
switchD_005c0b2f_caseD_80071f4b:
            return (int)"FRS_ERR_CHILD_TO_PARENT_COMM";
          case 0x1f4c:
switchD_005c0b2f_caseD_80071f4c:
            return (int)"FRS_ERR_PARENT_TO_CHILD_COMM";
          case 0x1f4d:
            goto switchD_005c750e_caseD_1f4d;
          case 0x1f4e:
            goto switchD_005c0b4d_caseD_80071f4e;
          }
        }
      }
      else if (in_stack_00000004 < 0x200f) {
        if (in_stack_00000004 == 0x200e) goto switchD_005c0b4d_caseD_8007200e;
        if (in_stack_00000004 < 0x200b) {
          if (in_stack_00000004 == 0x200a) goto switchD_005c0b4d_caseD_8007200a;
          if (in_stack_00000004 == 0x1f50) goto switchD_005c0b4d_caseD_80071f50;
          if (in_stack_00000004 == 0x1f51) goto switchD_005c0b4d_caseD_80071f51;
          if (in_stack_00000004 == 0x2008) goto switchD_005c0b4d_caseD_80072008;
          if (in_stack_00000004 == 0x2009) goto switchD_005c0b4d_caseD_80072009;
        }
        else {
          if (in_stack_00000004 == 0x200b) goto switchD_005c0b4d_caseD_8007200b;
          if (in_stack_00000004 == 0x200c) goto switchD_005c0b4d_caseD_8007200c;
          if (in_stack_00000004 == 0x200d) goto switchD_005c0b4d_caseD_8007200d;
        }
      }
      else {
        switch(in_stack_00000004) {
        case 0x200f:
          goto switchD_005c0b4d_caseD_8007200f;
        case 0x2010:
          goto switchD_005c0b4d_caseD_80072010;
        case 0x2011:
          goto switchD_005c0b4d_caseD_80072011;
        case 0x2012:
          goto switchD_005c0b4d_caseD_80072012;
        case 0x2013:
          goto switchD_005c0b4d_caseD_80072013;
        case 0x2014:
          goto switchD_005c0b4d_caseD_80072014;
        case 0x2015:
          goto switchD_005c0b4d_caseD_80072015;
        case 0x2016:
          goto switchD_005c0b4d_caseD_80072016;
        }
      }
    }
    else {
      switch(in_stack_00000004) {
      case 0x2018:
switchD_005c0b4d_caseD_80072018:
        return (int)"ERROR_DS_CROSS_DOM_MOVE_ERROR";
      case 0x2019:
switchD_005c0b4d_caseD_80072019:
        return (int)"ERROR_DS_GC_NOT_AVAILABLE";
      case 0x201a:
switchD_005c0b4d_caseD_8007201a:
        return (int)"ERROR_SHARED_POLICY";
      case 0x201b:
switchD_005c0b4d_caseD_8007201b:
        return (int)"ERROR_POLICY_OBJECT_NOT_FOUND";
      case 0x201c:
switchD_005c0b4d_caseD_8007201c:
        return (int)"ERROR_POLICY_ONLY_IN_DS";
      case 0x201d:
switchD_005c0b4d_caseD_8007201d:
        return (int)"ERROR_PROMOTION_ACTIVE";
      case 0x201e:
switchD_005c0b4d_caseD_8007201e:
        return (int)"ERROR_NO_PROMOTION_ACTIVE";
      case 0x2020:
switchD_005c0b4d_caseD_80072020:
        return (int)"ERROR_DS_OPERATIONS_ERROR";
      case 0x2021:
switchD_005c0b4d_caseD_80072021:
        return (int)"ERROR_DS_PROTOCOL_ERROR";
      case 0x2022:
switchD_005c0b4d_caseD_80072022:
        return (int)"ERROR_DS_TIMELIMIT_EXCEEDED";
      case 0x2023:
switchD_005c0b4d_caseD_80072023:
        return (int)"ERROR_DS_SIZELIMIT_EXCEEDED";
      case 0x2024:
switchD_005c0b4d_caseD_80072024:
        return (int)"ERROR_DS_ADMIN_LIMIT_EXCEEDED";
      case 0x2025:
switchD_005c0b4d_caseD_80072025:
        return (int)"ERROR_DS_COMPARE_FALSE";
      case 0x2026:
switchD_005c0b4d_caseD_80072026:
        return (int)"ERROR_DS_COMPARE_TRUE";
      case 0x2027:
switchD_005c0b4d_caseD_80072027:
        return (int)"ERROR_DS_AUTH_METHOD_NOT_SUPPORTED";
      case 0x2028:
switchD_005c0b4d_caseD_80072028:
        return (int)"ERROR_DS_STRONG_AUTH_REQUIRED";
      case 0x2029:
switchD_005c0b4d_caseD_80072029:
        return (int)"ERROR_DS_INAPPROPRIATE_AUTH";
      case 0x202a:
switchD_005c0b4d_caseD_8007202a:
        return (int)"ERROR_DS_AUTH_UNKNOWN";
      case 0x202b:
switchD_005c0b4d_caseD_8007202b:
        return (int)"ERROR_DS_REFERRAL";
      case 0x202c:
switchD_005c0b4d_caseD_8007202c:
        return (int)"ERROR_DS_UNAVAILABLE_CRIT_EXTENSION";
      case 0x202d:
switchD_005c0b4d_caseD_8007202d:
        return (int)"ERROR_DS_CONFIDENTIALITY_REQUIRED";
      case 0x202e:
switchD_005c0b4d_caseD_8007202e:
        return (int)"ERROR_DS_INAPPROPRIATE_MATCHING";
      case 0x202f:
switchD_005c0b4d_caseD_8007202f:
        return (int)"ERROR_DS_CONSTRAINT_VIOLATION";
      case 0x2030:
switchD_005c0b4d_caseD_80072030:
        return (int)"ERROR_DS_NO_SUCH_OBJECT";
      case 0x2031:
switchD_005c0b4d_caseD_80072031:
        return (int)"ERROR_DS_ALIAS_PROBLEM";
      case 0x2032:
switchD_005c0b4d_caseD_80072032:
        return (int)"ERROR_DS_INVALID_DN_SYNTAX";
      case 0x2033:
switchD_005c0b4d_caseD_80072033:
        return (int)"ERROR_DS_IS_LEAF";
      case 0x2034:
switchD_005c0b4d_caseD_80072034:
        return (int)"ERROR_DS_ALIAS_DEREF_PROBLEM";
      case 0x2035:
switchD_005c0b4d_caseD_80072035:
        return (int)"ERROR_DS_UNWILLING_TO_PERFORM";
      case 0x2036:
switchD_005c0b4d_caseD_80072036:
        return (int)"ERROR_DS_LOOP_DETECT";
      case 0x2037:
switchD_005c0b4d_caseD_80072037:
        return (int)"ERROR_DS_NAMING_VIOLATION";
      case 0x2038:
switchD_005c0b4d_caseD_80072038:
        return (int)"ERROR_DS_OBJECT_RESULTS_TOO_LARGE";
      case 0x2039:
switchD_005c768d_caseD_2039:
        return (int)"ERROR_DS_AFFECTS_MULTIPLE_DSAS";
      case 0x203a:
switchD_005c0b64_caseD_8007203a:
        return (int)"ERROR_DS_SERVER_DOWN";
      case 0x203b:
switchD_005c0b64_caseD_8007203b:
        return (int)"ERROR_DS_LOCAL_ERROR";
      case 0x203c:
switchD_005c0b64_caseD_8007203c:
        return (int)"ERROR_DS_ENCODING_ERROR";
      case 0x203d:
switchD_005c0b64_caseD_8007203d:
        return (int)"ERROR_DS_DECODING_ERROR";
      case 0x203e:
switchD_005c0b64_caseD_8007203e:
        return (int)"ERROR_DS_FILTER_UNKNOWN";
      case 0x203f:
switchD_005c0b64_caseD_8007203f:
        return (int)"ERROR_DS_PARAM_ERROR";
      case 0x2040:
switchD_005c0b64_caseD_80072040:
        return (int)"ERROR_DS_NOT_SUPPORTED";
      case 0x2041:
switchD_005c0b64_caseD_80072041:
        return (int)"ERROR_DS_NO_RESULTS_RETURNED";
      case 0x2042:
switchD_005c0b64_caseD_80072042:
        return (int)"ERROR_DS_CONTROL_NOT_FOUND";
      case 0x2043:
switchD_005c0b64_caseD_80072043:
        return (int)"ERROR_DS_CLIENT_LOOP";
      case 0x2044:
switchD_005c0b64_caseD_80072044:
        return (int)"ERROR_DS_REFERRAL_LIMIT_EXCEEDED";
      case 0x2045:
switchD_005c0b64_caseD_80072045:
        return (int)"ERROR_DS_SORT_CONTROL_MISSING";
      case 0x2046:
switchD_005c0b64_caseD_80072046:
        return (int)"ERROR_DS_OFFSET_RANGE_ERROR";
      case 0x206d:
switchD_005c0b64_caseD_8007206d:
        return (int)"ERROR_DS_ROOT_MUST_BE_NC";
      case 0x206e:
switchD_005c0b64_caseD_8007206e:
        return (int)"ERROR_DS_ADD_REPLICA_INHIBITED";
      case 0x206f:
switchD_005c0b64_caseD_8007206f:
        return (int)"ERROR_DS_ATT_NOT_DEF_IN_SCHEMA";
      case 0x2070:
switchD_005c0b64_caseD_80072070:
        return (int)"ERROR_DS_MAX_OBJ_SIZE_EXCEEDED";
      case 0x2071:
switchD_005c0b64_caseD_80072071:
        return (int)"ERROR_DS_OBJ_STRING_NAME_EXISTS";
      case 0x2072:
switchD_005c0b64_caseD_80072072:
        return (int)"ERROR_DS_NO_RDN_DEFINED_IN_SCHEMA";
      case 0x2073:
switchD_005c0b64_caseD_80072073:
        return (int)"ERROR_DS_RDN_DOESNT_MATCH_SCHEMA";
      case 0x2074:
switchD_005c0b64_caseD_80072074:
        return (int)"ERROR_DS_NO_REQUESTED_ATTS_FOUND";
      case 0x2075:
switchD_005c0b64_caseD_80072075:
        return (int)"ERROR_DS_USER_BUFFER_TO_SMALL";
      case 0x2076:
switchD_005c0b64_caseD_80072076:
        return (int)"ERROR_DS_ATT_IS_NOT_ON_OBJ";
      case 0x2077:
switchD_005c0b64_caseD_80072077:
        return (int)"ERROR_DS_ILLEGAL_MOD_OPERATION";
      case 0x2078:
switchD_005c0b64_caseD_80072078:
        return (int)"ERROR_DS_OBJ_TOO_LARGE";
      case 0x2079:
switchD_005c0b64_caseD_80072079:
        return (int)"ERROR_DS_BAD_INSTANCE_TYPE";
      case 0x207a:
switchD_005c0b64_caseD_8007207a:
        return (int)"ERROR_DS_MASTERDSA_REQUIRED";
      case 0x207b:
switchD_005c0b64_caseD_8007207b:
        return (int)"ERROR_DS_OBJECT_CLASS_REQUIRED";
      case 0x207c:
switchD_005c0b64_caseD_8007207c:
        return (int)"ERROR_DS_MISSING_REQUIRED_ATT";
      case 0x207d:
switchD_005c0b64_caseD_8007207d:
        return (int)"ERROR_DS_ATT_NOT_DEF_FOR_CLASS";
      case 0x207e:
switchD_005c0b64_caseD_8007207e:
        return (int)"ERROR_DS_ATT_ALREADY_EXISTS";
      case 0x2080:
switchD_005c0b64_caseD_80072080:
        return (int)"ERROR_DS_CANT_ADD_ATT_VALUES";
      case 0x2081:
switchD_005c0b64_caseD_80072081:
        return (int)"ERROR_DS_SINGLE_VALUE_CONSTRAINT";
      case 0x2082:
switchD_005c0b64_caseD_80072082:
        return (int)"ERROR_DS_RANGE_CONSTRAINT";
      case 0x2083:
switchD_005c0b64_caseD_80072083:
        return (int)"ERROR_DS_ATT_VAL_ALREADY_EXISTS";
      case 0x2084:
switchD_005c0b64_caseD_80072084:
        return (int)"ERROR_DS_CANT_REM_MISSING_ATT";
      case 0x2085:
switchD_005c0b64_caseD_80072085:
        return (int)"ERROR_DS_CANT_REM_MISSING_ATT_VAL";
      case 0x2086:
switchD_005c0b64_caseD_80072086:
        return (int)"ERROR_DS_ROOT_CANT_BE_SUBREF";
      case 0x2087:
switchD_005c0b64_caseD_80072087:
        return (int)"ERROR_DS_NO_CHAINING";
      case 0x2088:
switchD_005c0b64_caseD_80072088:
        return (int)"ERROR_DS_NO_CHAINED_EVAL";
      case 0x2089:
switchD_005c0b64_caseD_80072089:
        return (int)"ERROR_DS_NO_PARENT_OBJECT";
      case 0x208a:
switchD_005c0b64_caseD_8007208a:
        return (int)"ERROR_DS_PARENT_IS_AN_ALIAS";
      case 0x208b:
switchD_005c0b64_caseD_8007208b:
        return (int)"ERROR_DS_CANT_MIX_MASTER_AND_REPS";
      case 0x208c:
switchD_005c0b64_caseD_8007208c:
        return (int)"ERROR_DS_CHILDREN_EXIST";
      case 0x208d:
switchD_005c0b64_caseD_8007208d:
        return (int)"ERROR_DS_OBJ_NOT_FOUND";
      case 0x208e:
switchD_005c0b64_caseD_8007208e:
        return (int)"ERROR_DS_ALIASED_OBJ_MISSING";
      case 0x208f:
switchD_005c0b64_caseD_8007208f:
        return (int)"ERROR_DS_BAD_NAME_SYNTAX";
      case 0x2090:
switchD_005c0b64_caseD_80072090:
        return (int)"ERROR_DS_ALIAS_POINTS_TO_ALIAS";
      case 0x2091:
switchD_005c0b64_caseD_80072091:
        return (int)"ERROR_DS_CANT_DEREF_ALIAS";
      case 0x2092:
switchD_005c0b64_caseD_80072092:
        return (int)"ERROR_DS_OUT_OF_SCOPE";
      case 0x2093:
switchD_005c0b64_caseD_80072093:
        return (int)"ERROR_DS_OBJECT_BEING_REMOVED";
      case 0x2094:
switchD_005c0b64_caseD_80072094:
        return (int)"ERROR_DS_CANT_DELETE_DSA_OBJ";
      case 0x2095:
switchD_005c0b64_caseD_80072095:
        return (int)"ERROR_DS_GENERIC_ERROR";
      case 0x2096:
switchD_005c0b64_caseD_80072096:
        return (int)"ERROR_DS_DSA_MUST_BE_INT_MASTER";
      case 0x2097:
switchD_005c0b64_caseD_80072097:
        return (int)"ERROR_DS_CLASS_NOT_DSA";
      case 0x2098:
switchD_005c0b64_caseD_80072098:
        return (int)"ERROR_DS_INSUFF_ACCESS_RIGHTS";
      case 0x2099:
switchD_005c0b64_caseD_80072099:
        return (int)"ERROR_DS_ILLEGAL_SUPERIOR";
      case 0x209a:
switchD_005c0b64_caseD_8007209a:
        return (int)"ERROR_DS_ATTRIBUTE_OWNED_BY_SAM";
      case 0x209b:
switchD_005c0b64_caseD_8007209b:
        return (int)"ERROR_DS_NAME_TOO_MANY_PARTS";
      case 0x209c:
switchD_005c0b64_caseD_8007209c:
        return (int)"ERROR_DS_NAME_TOO_LONG";
      case 0x209d:
switchD_005c0b64_caseD_8007209d:
        return (int)"ERROR_DS_NAME_VALUE_TOO_LONG";
      case 0x209e:
switchD_005c0b64_caseD_8007209e:
        return (int)"ERROR_DS_NAME_UNPARSEABLE";
      case 0x209f:
switchD_005c0b64_caseD_8007209f:
        return (int)"ERROR_DS_NAME_TYPE_UNKNOWN";
      case 0x20a0:
switchD_005c0b64_caseD_800720a0:
        return (int)"ERROR_DS_NOT_AN_OBJECT";
      case 0x20a1:
switchD_005c0b64_caseD_800720a1:
        return (int)"ERROR_DS_SEC_DESC_TOO_SHORT";
      case 0x20a2:
switchD_005c0b64_caseD_800720a2:
        return (int)"ERROR_DS_SEC_DESC_INVALID";
      case 0x20a3:
switchD_005c0b64_caseD_800720a3:
        return (int)"ERROR_DS_NO_DELETED_NAME";
      case 0x20a4:
switchD_005c0b64_caseD_800720a4:
        return (int)"ERROR_DS_SUBREF_MUST_HAVE_PARENT";
      case 0x20a5:
switchD_005c0b64_caseD_800720a5:
        return (int)"ERROR_DS_NCNAME_MUST_BE_NC";
      case 0x20a6:
switchD_005c0b64_caseD_800720a6:
        return (int)"ERROR_DS_CANT_ADD_SYSTEM_ONLY";
      case 0x20a7:
switchD_005c0b64_caseD_800720a7:
        return (int)"ERROR_DS_CLASS_MUST_BE_CONCRETE";
      case 0x20a8:
switchD_005c0b64_caseD_800720a8:
        return (int)"ERROR_DS_INVALID_DMD";
      case 0x20a9:
switchD_005c0b64_caseD_800720a9:
        return (int)"ERROR_DS_OBJ_GUID_EXISTS";
      case 0x20aa:
switchD_005c0b64_caseD_800720aa:
        return (int)"ERROR_DS_NOT_ON_BACKLINK";
      case 0x20ab:
switchD_005c0b64_caseD_800720ab:
        return (int)"ERROR_DS_NO_CROSSREF_FOR_NC";
      case 0x20ac:
switchD_005c0b64_caseD_800720ac:
        return (int)"ERROR_DS_SHUTTING_DOWN";
      case 0x20ad:
switchD_005c0b64_caseD_800720ad:
        return (int)"ERROR_DS_UNKNOWN_OPERATION";
      case 0x20ae:
switchD_005c0b64_caseD_800720ae:
        return (int)"ERROR_DS_INVALID_ROLE_OWNER";
      case 0x20af:
switchD_005c0b64_caseD_800720af:
        return (int)"ERROR_DS_COULDNT_CONTACT_FSMO";
      case 0x20b0:
switchD_005c0b64_caseD_800720b0:
        return (int)"ERROR_DS_CROSS_NC_DN_RENAME";
      case 0x20b1:
switchD_005c0b64_caseD_800720b1:
        return (int)"ERROR_DS_CANT_MOD_SYSTEM_ONLY";
      case 0x20b2:
switchD_005c0b64_caseD_800720b2:
        return (int)"ERROR_DS_REPLICATOR_ONLY";
      case 0x20b3:
switchD_005c0b64_caseD_800720b3:
        return (int)"ERROR_DS_OBJ_CLASS_NOT_DEFINED";
      case 0x20b4:
switchD_005c0b64_caseD_800720b4:
        return (int)"ERROR_DS_OBJ_CLASS_NOT_SUBCLASS";
      case 0x20b5:
switchD_005c0b64_caseD_800720b5:
        return (int)"ERROR_DS_NAME_REFERENCE_INVALID";
      case 0x20b6:
switchD_005c0b64_caseD_800720b6:
        return (int)"ERROR_DS_CROSS_REF_EXISTS";
      case 0x20b7:
switchD_005c0b64_caseD_800720b7:
        return (int)"ERROR_DS_CANT_DEL_MASTER_CROSSREF";
      case 0x20b8:
switchD_005c0b64_caseD_800720b8:
        return (int)"ERROR_DS_SUBTREE_NOTIFY_NOT_NC_HEAD";
      case 0x20b9:
switchD_005c0b64_caseD_800720b9:
        return (int)"ERROR_DS_NOTIFY_FILTER_TOO_COMPLEX";
      case 0x20ba:
switchD_005c0b64_caseD_800720ba:
        return (int)"ERROR_DS_DUP_RDN";
      case 0x20bb:
switchD_005c0b64_caseD_800720bb:
        return (int)"ERROR_DS_DUP_OID";
      case 0x20bc:
switchD_005c0b64_caseD_800720bc:
        return (int)"ERROR_DS_DUP_MAPI_ID";
      case 0x20bd:
switchD_005c0b64_caseD_800720bd:
        return (int)"ERROR_DS_DUP_SCHEMA_ID_GUID";
      case 0x20be:
switchD_005c0b64_caseD_800720be:
        return (int)"ERROR_DS_DUP_LDAP_DISPLAY_NAME";
      case 0x20bf:
switchD_005c0b64_caseD_800720bf:
        return (int)"ERROR_DS_SEMANTIC_ATT_TEST";
      case 0x20c0:
switchD_005c0b64_caseD_800720c0:
        return (int)"ERROR_DS_SYNTAX_MISMATCH";
      case 0x20c1:
switchD_005c0b64_caseD_800720c1:
        return (int)"ERROR_DS_EXISTS_IN_MUST_HAVE";
      case 0x20c2:
switchD_005c0b64_caseD_800720c2:
        return (int)"ERROR_DS_EXISTS_IN_MAY_HAVE";
      case 0x20c3:
switchD_005c0b64_caseD_800720c3:
        return (int)"ERROR_DS_NONEXISTENT_MAY_HAVE";
      case 0x20c4:
switchD_005c0b64_caseD_800720c4:
        return (int)"ERROR_DS_NONEXISTENT_MUST_HAVE";
      case 0x20c5:
switchD_005c0b64_caseD_800720c5:
        return (int)"ERROR_DS_AUX_CLS_TEST_FAIL";
      case 0x20c6:
switchD_005c0b64_caseD_800720c6:
        return (int)"ERROR_DS_NONEXISTENT_POSS_SUP";
      case 0x20c7:
switchD_005c0b64_caseD_800720c7:
        return (int)"ERROR_DS_SUB_CLS_TEST_FAIL";
      case 0x20c8:
switchD_005c0b64_caseD_800720c8:
        return (int)"ERROR_DS_BAD_RDN_ATT_ID_SYNTAX";
      case 0x20c9:
switchD_005c0b64_caseD_800720c9:
        return (int)"ERROR_DS_EXISTS_IN_AUX_CLS";
      case 0x20ca:
switchD_005c0b64_caseD_800720ca:
        return (int)"ERROR_DS_EXISTS_IN_SUB_CLS";
      case 0x20cb:
switchD_005c0b64_caseD_800720cb:
        return (int)"ERROR_DS_EXISTS_IN_POSS_SUP";
      case 0x20cc:
switchD_005c0b64_caseD_800720cc:
        return (int)"ERROR_DS_RECALCSCHEMA_FAILED";
      case 0x20cd:
switchD_005c0b64_caseD_800720cd:
        return (int)"ERROR_DS_TREE_DELETE_NOT_FINISHED";
      case 0x20ce:
switchD_005c0b64_caseD_800720ce:
        return (int)"ERROR_DS_CANT_DELETE";
      case 0x20cf:
switchD_005c0b64_caseD_800720cf:
        return (int)"ERROR_DS_ATT_SCHEMA_REQ_ID";
      case 0x20d0:
switchD_005c0b64_caseD_800720d0:
        return (int)"ERROR_DS_BAD_ATT_SCHEMA_SYNTAX";
      case 0x20d1:
switchD_005c0b64_caseD_800720d1:
        return (int)"ERROR_DS_CANT_CACHE_ATT";
      case 0x20d2:
switchD_005c0b64_caseD_800720d2:
        return (int)"ERROR_DS_CANT_CACHE_CLASS";
      case 0x20d3:
switchD_005c0b64_caseD_800720d3:
        return (int)"ERROR_DS_CANT_REMOVE_ATT_CACHE";
      case 0x20d4:
switchD_005c0b64_caseD_800720d4:
        return (int)"ERROR_DS_CANT_REMOVE_CLASS_CACHE";
      case 0x20d5:
switchD_005c0b64_caseD_800720d5:
        return (int)"ERROR_DS_CANT_RETRIEVE_DN";
      case 0x20d6:
switchD_005c0b64_caseD_800720d6:
        return (int)"ERROR_DS_MISSING_SUPREF";
      case 0x20d7:
switchD_005c0b64_caseD_800720d7:
        return (int)"ERROR_DS_CANT_RETRIEVE_INSTANCE";
      case 0x20d8:
switchD_005c0b64_caseD_800720d8:
        return (int)"ERROR_DS_CODE_INCONSISTENCY";
      case 0x20d9:
switchD_005c0b64_caseD_800720d9:
        return (int)"ERROR_DS_DATABASE_ERROR";
      case 0x20da:
switchD_005c0b64_caseD_800720da:
        return (int)"ERROR_DS_GOVERNSID_MISSING";
      case 0x20db:
switchD_005c0b64_caseD_800720db:
        return (int)"ERROR_DS_MISSING_EXPECTED_ATT";
      case 0x20dc:
switchD_005c0b64_caseD_800720dc:
        return (int)"ERROR_DS_NCNAME_MISSING_CR_REF";
      case 0x20dd:
switchD_005c0b64_caseD_800720dd:
        return (int)"ERROR_DS_SECURITY_CHECKING_ERROR";
      case 0x20de:
switchD_005c0b64_caseD_800720de:
        return (int)"ERROR_DS_SCHEMA_NOT_LOADED";
      case 0x20df:
switchD_005c0b64_caseD_800720df:
        return (int)"ERROR_DS_SCHEMA_ALLOC_FAILED";
      case 0x20e0:
switchD_005c0b64_caseD_800720e0:
        return (int)"ERROR_DS_ATT_SCHEMA_REQ_SYNTAX";
      case 0x20e1:
switchD_005c0b64_caseD_800720e1:
        return (int)"ERROR_DS_GCVERIFY_ERROR";
      case 0x20e2:
switchD_005c0b64_caseD_800720e2:
        return (int)"ERROR_DS_DRA_SCHEMA_MISMATCH";
      case 0x20e3:
switchD_005c0b64_caseD_800720e3:
        return (int)"ERROR_DS_CANT_FIND_DSA_OBJ";
      case 0x20e4:
switchD_005c0b64_caseD_800720e4:
        return (int)"ERROR_DS_CANT_FIND_EXPECTED_NC";
      case 0x20e5:
switchD_005c0b64_caseD_800720e5:
        return (int)"ERROR_DS_CANT_FIND_NC_IN_CACHE";
      case 0x20e6:
switchD_005c0b64_caseD_800720e6:
        return (int)"ERROR_DS_CANT_RETRIEVE_CHILD";
      case 0x20e7:
switchD_005c0b64_caseD_800720e7:
        return (int)"ERROR_DS_SECURITY_ILLEGAL_MODIFY";
      case 0x20e8:
switchD_005c0b64_caseD_800720e8:
        return (int)"ERROR_DS_CANT_REPLACE_HIDDEN_REC";
      case 0x20e9:
switchD_005c0b64_caseD_800720e9:
        return (int)"ERROR_DS_BAD_HIERARCHY_FILE";
      case 0x20ea:
switchD_005c0b64_caseD_800720ea:
        return (int)"ERROR_DS_BUILD_HIERARCHY_TABLE_FAILED";
      case 0x20eb:
switchD_005c0b64_caseD_800720eb:
        return (int)"ERROR_DS_CONFIG_PARAM_MISSING";
      case 0x20ec:
switchD_005c0b64_caseD_800720ec:
        return (int)"ERROR_DS_COUNTING_AB_INDICES_FAILED";
      case 0x20ed:
switchD_005c0b64_caseD_800720ed:
        return (int)"ERROR_DS_HIERARCHY_TABLE_MALLOC_FAILED";
      case 0x20ee:
switchD_005c0b64_caseD_800720ee:
        return (int)"ERROR_DS_INTERNAL_FAILURE";
      case 0x20ef:
switchD_005c0b64_caseD_800720ef:
        return (int)"ERROR_DS_UNKNOWN_ERROR";
      case 0x20f0:
switchD_005c0b64_caseD_800720f0:
        return (int)"ERROR_DS_ROOT_REQUIRES_CLASS_TOP";
      case 0x20f1:
switchD_005c0b64_caseD_800720f1:
        return (int)"ERROR_DS_REFUSING_FSMO_ROLES";
      case 0x20f2:
switchD_005c0b64_caseD_800720f2:
        return (int)"ERROR_DS_MISSING_FSMO_SETTINGS";
      case 0x20f3:
switchD_005c0b64_caseD_800720f3:
        return (int)"ERROR_DS_UNABLE_TO_SURRENDER_ROLES";
      case 0x20f4:
switchD_005c0b64_caseD_800720f4:
        return (int)"ERROR_DS_DRA_GENERIC";
      case 0x20f5:
switchD_005c0b64_caseD_800720f5:
        return (int)"ERROR_DS_DRA_INVALID_PARAMETER";
      case 0x20f6:
switchD_005c0b64_caseD_800720f6:
        return (int)"ERROR_DS_DRA_BUSY";
      case 0x20f7:
switchD_005c0b64_caseD_800720f7:
        return (int)"ERROR_DS_DRA_BAD_DN";
      case 0x20f8:
switchD_005c0b64_caseD_800720f8:
        return (int)"ERROR_DS_DRA_BAD_NC";
      case 0x20f9:
switchD_005c0b64_caseD_800720f9:
        return (int)"ERROR_DS_DRA_DN_EXISTS";
      case 0x20fa:
switchD_005c0b64_caseD_800720fa:
        return (int)"ERROR_DS_DRA_INTERNAL_ERROR";
      case 0x20fb:
switchD_005c0b64_caseD_800720fb:
        return (int)"ERROR_DS_DRA_INCONSISTENT_DIT";
      case 0x20fc:
switchD_005c0b64_caseD_800720fc:
        return (int)"ERROR_DS_DRA_CONNECTION_FAILED";
      case 0x20fd:
switchD_005c0b64_caseD_800720fd:
        return (int)"ERROR_DS_DRA_BAD_INSTANCE_TYPE";
      case 0x20fe:
switchD_005c0b64_caseD_800720fe:
        return (int)"ERROR_DS_DRA_OUT_OF_MEM";
      case 0x20ff:
switchD_005c0b64_caseD_800720ff:
        return (int)"ERROR_DS_DRA_MAIL_PROBLEM";
      case 0x2100:
switchD_005c0b64_caseD_80072100:
        return (int)"ERROR_DS_DRA_REF_ALREADY_EXISTS";
      case 0x2101:
switchD_005c0b64_caseD_80072101:
        return (int)"ERROR_DS_DRA_REF_NOT_FOUND";
      case 0x2102:
switchD_005c0b64_caseD_80072102:
        return (int)"ERROR_DS_DRA_OBJ_IS_REP_SOURCE";
      case 0x2103:
switchD_005c0b64_caseD_80072103:
        return (int)"ERROR_DS_DRA_DB_ERROR";
      case 0x2104:
switchD_005c0b64_caseD_80072104:
        return (int)"ERROR_DS_DRA_NO_REPLICA";
      case 0x2105:
switchD_005c0b64_caseD_80072105:
        return (int)"ERROR_DS_DRA_ACCESS_DENIED";
      case 0x2106:
switchD_005c0b64_caseD_80072106:
        return (int)"ERROR_DS_DRA_NOT_SUPPORTED";
      case 0x2107:
switchD_005c0b64_caseD_80072107:
        return (int)"ERROR_DS_DRA_RPC_CANCELLED";
      case 0x2108:
switchD_005c0b64_caseD_80072108:
        return (int)"ERROR_DS_DRA_SOURCE_DISABLED";
      case 0x2109:
switchD_005c0b64_caseD_80072109:
        return (int)"ERROR_DS_DRA_SINK_DISABLED";
      case 0x210a:
switchD_005c0b64_caseD_8007210a:
        return (int)"ERROR_DS_DRA_NAME_COLLISION";
      case 0x210b:
switchD_005c0b64_caseD_8007210b:
        return (int)"ERROR_DS_DRA_SOURCE_REINSTALLED";
      case 0x210c:
switchD_005c0b64_caseD_8007210c:
        return (int)"ERROR_DS_DRA_MISSING_PARENT";
      case 0x210d:
switchD_005c0b64_caseD_8007210d:
        return (int)"ERROR_DS_DRA_PREEMPTED";
      case 0x210e:
switchD_005c0b64_caseD_8007210e:
        return (int)"ERROR_DS_DRA_ABANDON_SYNC";
      case 0x210f:
switchD_005c0b64_caseD_8007210f:
        return (int)"ERROR_DS_DRA_SHUTDOWN";
      case 0x2110:
switchD_005c0b64_caseD_80072110:
        return (int)"ERROR_DS_DRA_INCOMPATIBLE_PARTIAL_SET";
      case 0x2111:
switchD_005c0b64_caseD_80072111:
        return (int)"ERROR_DS_DRA_SOURCE_IS_PARTIAL_REPLICA";
      case 0x2112:
switchD_005c0b64_caseD_80072112:
        return (int)"ERROR_DS_DRA_EXTN_CONNECTION_FAILED";
      case 0x2113:
switchD_005c0b64_caseD_80072113:
        return (int)"ERROR_DS_INSTALL_SCHEMA_MISMATCH";
      case 0x2114:
switchD_005c0b64_caseD_80072114:
        return (int)"ERROR_DS_DUP_LINK_ID";
      case 0x2115:
switchD_005c0b64_caseD_80072115:
        return (int)"ERROR_DS_NAME_ERROR_RESOLVING";
      case 0x2116:
switchD_005c0b64_caseD_80072116:
        return (int)"ERROR_DS_NAME_ERROR_NOT_FOUND";
      case 0x2117:
switchD_005c0b64_caseD_80072117:
        return (int)"ERROR_DS_NAME_ERROR_NOT_UNIQUE";
      case 0x2118:
switchD_005c0b64_caseD_80072118:
        return (int)"ERROR_DS_NAME_ERROR_NO_MAPPING";
      case 0x2119:
switchD_005c0b64_caseD_80072119:
        return (int)"ERROR_DS_NAME_ERROR_DOMAIN_ONLY";
      case 0x211a:
switchD_005c0b64_caseD_8007211a:
        return (int)"ERROR_DS_NAME_ERROR_NO_SYNTACTICAL_MAPPING";
      case 0x211b:
switchD_005c0b64_caseD_8007211b:
        return (int)"ERROR_DS_CONSTRUCTED_ATT_MOD";
      case 0x211c:
switchD_005c0b64_caseD_8007211c:
        return (int)"ERROR_DS_WRONG_OM_OBJ_CLASS";
      case 0x211d:
switchD_005c0b64_caseD_8007211d:
        return (int)"ERROR_DS_DRA_REPL_PENDING";
      case 0x211e:
switchD_005c0b64_caseD_8007211e:
        return (int)"ERROR_DS_DS_REQUIRED";
      case 0x211f:
switchD_005c0b64_caseD_8007211f:
        return (int)"ERROR_DS_INVALID_LDAP_DISPLAY_NAME";
      case 0x2120:
switchD_005c0b64_caseD_80072120:
        return (int)"ERROR_DS_NON_BASE_SEARCH";
      case 0x2121:
switchD_005c0b64_caseD_80072121:
        return (int)"ERROR_DS_CANT_RETRIEVE_ATTS";
      case 0x2122:
switchD_005c0b64_caseD_80072122:
        return (int)"ERROR_DS_BACKLINK_WITHOUT_LINK";
      case 0x2123:
switchD_005c0b64_caseD_80072123:
        return (int)"ERROR_DS_EPOCH_MISMATCH";
      case 0x2124:
switchD_005c0b64_caseD_80072124:
        return (int)"ERROR_DS_SRC_NAME_MISMATCH";
      case 0x2125:
switchD_005c0b64_caseD_80072125:
        return (int)"ERROR_DS_SRC_AND_DST_NC_IDENTICAL";
      case 0x2126:
switchD_005c0b64_caseD_80072126:
        return (int)"ERROR_DS_DST_NC_MISMATCH";
      case 0x2127:
switchD_005c0b64_caseD_80072127:
        return (int)"ERROR_DS_NOT_AUTHORITIVE_FOR_DST_NC";
      case 0x2128:
switchD_005c0b64_caseD_80072128:
        return (int)"ERROR_DS_SRC_GUID_MISMATCH";
      case 0x2129:
switchD_005c0b64_caseD_80072129:
        return (int)"ERROR_DS_CANT_MOVE_DELETED_OBJECT";
      case 0x212a:
switchD_005c0b64_caseD_8007212a:
        return (int)"ERROR_DS_PDC_OPERATION_IN_PROGRESS";
      case 0x212b:
switchD_005c0b64_caseD_8007212b:
        return (int)"ERROR_DS_CROSS_DOMAIN_CLEANUP_REQD";
      case 0x212c:
switchD_005c0b64_caseD_8007212c:
        return (int)"ERROR_DS_ILLEGAL_XDOM_MOVE_OPERATION";
      case 0x212d:
switchD_005c0b64_caseD_8007212d:
        return (int)"ERROR_DS_CANT_WITH_ACCT_GROUP_MEMBERSHPS";
      case 0x212e:
switchD_005c0b64_caseD_8007212e:
        return (int)"ERROR_DS_NC_MUST_HAVE_NC_PARENT";
      case 0x212f:
switchD_005c0b64_caseD_8007212f:
        return (int)"ERROR_DS_CR_IMPOSSIBLE_TO_VALIDATE";
      case 0x2130:
switchD_005c0b64_caseD_80072130:
        return (int)"ERROR_DS_DST_DOMAIN_NOT_NATIVE";
      case 0x2131:
switchD_005c0b64_caseD_80072131:
        return (int)"ERROR_DS_MISSING_INFRASTRUCTURE_CONTAINER";
      case 0x2132:
switchD_005c0b64_caseD_80072132:
        return (int)"ERROR_DS_CANT_MOVE_ACCOUNT_GROUP";
      case 0x2133:
switchD_005c0b64_caseD_80072133:
        return (int)"ERROR_DS_CANT_MOVE_RESOURCE_GROUP";
      case 0x2134:
switchD_005c0b64_caseD_80072134:
        return (int)"ERROR_DS_INVALID_SEARCH_FLAG";
      case 0x2135:
switchD_005c0b64_caseD_80072135:
        return (int)"ERROR_DS_NO_TREE_DELETE_ABOVE_NC";
      case 0x2136:
switchD_005c0b64_caseD_80072136:
        return (int)"ERROR_DS_COULDNT_LOCK_TREE_FOR_DELETE";
      case 0x2137:
switchD_005c0b64_caseD_80072137:
        return (int)"ERROR_DS_COULDNT_IDENTIFY_OBJECTS_FOR_TREE_DELETE";
      case 0x2138:
switchD_005c0b64_caseD_80072138:
        return (int)"ERROR_DS_SAM_INIT_FAILURE";
      case 0x2139:
switchD_005c0b64_caseD_80072139:
        return (int)"ERROR_DS_SENSITIVE_GROUP_VIOLATION";
      case 0x213a:
switchD_005c0b64_caseD_8007213a:
        return (int)"ERROR_DS_CANT_MOD_PRIMARYGROUPID";
      case 0x213b:
switchD_005c0b64_caseD_8007213b:
        return (int)"ERROR_DS_ILLEGAL_BASE_SCHEMA_MOD";
      case 0x213c:
switchD_005c0b64_caseD_8007213c:
        return (int)"ERROR_DS_NONSAFE_SCHEMA_CHANGE";
      case 0x213d:
switchD_005c0b64_caseD_8007213d:
        return (int)"ERROR_DS_SCHEMA_UPDATE_DISALLOWED";
      case 0x213e:
switchD_005c0b64_caseD_8007213e:
        return (int)"ERROR_DS_CANT_CREATE_UNDER_SCHEMA";
      case 0x213f:
switchD_005c0b64_caseD_8007213f:
        return (int)"ERROR_DS_INSTALL_NO_SRC_SCH_VERSION";
      case 0x2140:
switchD_005c0b64_caseD_80072140:
        return (int)"ERROR_DS_INSTALL_NO_SCH_VERSION_IN_INIFILE";
      case 0x2141:
switchD_005c0b64_caseD_80072141:
        return (int)"ERROR_DS_INVALID_GROUP_TYPE";
      case 0x2142:
switchD_005c0b64_caseD_80072142:
        return (int)"ERROR_DS_NO_NEST_GLOBALGROUP_IN_MIXEDDOMAIN";
      case 0x2143:
switchD_005c0b64_caseD_80072143:
        return (int)"ERROR_DS_NO_NEST_LOCALGROUP_IN_MIXEDDOMAIN";
      case 0x2144:
switchD_005c0b64_caseD_80072144:
        return (int)"ERROR_DS_GLOBAL_CANT_HAVE_LOCAL_MEMBER";
      case 0x2145:
switchD_005c0b64_caseD_80072145:
        return (int)"ERROR_DS_GLOBAL_CANT_HAVE_UNIVERSAL_MEMBER";
      case 0x2146:
switchD_005c0b64_caseD_80072146:
        return (int)"ERROR_DS_UNIVERSAL_CANT_HAVE_LOCAL_MEMBER";
      case 0x2147:
switchD_005c0b64_caseD_80072147:
        return (int)"ERROR_DS_GLOBAL_CANT_HAVE_CROSSDOMAIN_MEMBER";
      case 0x2148:
switchD_005c0b64_caseD_80072148:
        return (int)"ERROR_DS_LOCAL_CANT_HAVE_CROSSDOMAIN_LOCAL_MEMBER";
      case 0x2149:
switchD_005c0b64_caseD_80072149:
        return (int)"ERROR_DS_HAVE_PRIMARY_MEMBERS";
      case 0x214a:
switchD_005c0b64_caseD_8007214a:
        return (int)"ERROR_DS_STRING_SD_CONVERSION_FAILED";
      case 0x214b:
switchD_005c0b64_caseD_8007214b:
        return (int)"ERROR_DS_NAMING_MASTER_GC";
      case 0x214c:
switchD_005c0b64_caseD_8007214c:
        return (int)"ERROR_DS_DNS_LOOKUP_FAILURE";
      case 0x214d:
switchD_005c0b64_caseD_8007214d:
        return (int)"ERROR_DS_COULDNT_UPDATE_SPNS";
      case 0x214e:
switchD_005c0b64_caseD_8007214e:
        return (int)"ERROR_DS_CANT_RETRIEVE_SD";
      case 0x214f:
switchD_005c0b64_caseD_8007214f:
        return (int)"ERROR_DS_KEY_NOT_UNIQUE";
      case 0x2150:
switchD_005c0b64_caseD_80072150:
        return (int)"ERROR_DS_WRONG_LINKED_ATT_SYNTAX";
      case 0x2151:
switchD_005c0b64_caseD_80072151:
        return (int)"ERROR_DS_SAM_NEED_BOOTKEY_PASSWORD";
      case 0x2152:
switchD_005c0b64_caseD_80072152:
        return (int)"ERROR_DS_SAM_NEED_BOOTKEY_FLOPPY";
      case 0x2153:
switchD_005c0b64_caseD_80072153:
        return (int)"ERROR_DS_CANT_START";
      case 0x2154:
switchD_005c0b64_caseD_80072154:
        return (int)"ERROR_DS_INIT_FAILURE";
      case 0x2155:
switchD_005c0b64_caseD_80072155:
        return (int)"ERROR_DS_NO_PKT_PRIVACY_ON_CONNECTION";
      case 0x2156:
switchD_005c0b64_caseD_80072156:
        return (int)"ERROR_DS_SOURCE_DOMAIN_IN_FOREST";
      case 0x2157:
switchD_005c0b64_caseD_80072157:
        return (int)"ERROR_DS_DESTINATION_DOMAIN_NOT_IN_FOREST";
      case 0x2158:
switchD_005c0b64_caseD_80072158:
        return (int)"ERROR_DS_DESTINATION_AUDITING_NOT_ENABLED";
      case 0x2159:
switchD_005c0b64_caseD_80072159:
        return (int)"ERROR_DS_CANT_FIND_DC_FOR_SRC_DOMAIN";
      case 0x215a:
switchD_005c0b64_caseD_8007215a:
        return (int)"ERROR_DS_SRC_OBJ_NOT_GROUP_OR_USER";
      case 0x215b:
switchD_005c0b64_caseD_8007215b:
        return (int)"ERROR_DS_SRC_SID_EXISTS_IN_FOREST";
      case 0x215c:
switchD_005c0b64_caseD_8007215c:
        return (int)"ERROR_DS_SRC_AND_DST_OBJECT_CLASS_MISMATCH";
      }
    }
  }
  else if (in_stack_00000004 < 0x2329) {
    if (in_stack_00000004 == 9000) {
LAB_005c84b8:
      return (int)"DNS_ERROR_RESPONSE_CODES_BASE";
    }
    switch(in_stack_00000004) {
    case 0x215e:
switchD_005c0b64_caseD_8007215e:
      return (int)"ERROR_DS_DRA_SCHEMA_INFO_SHIP";
    case 0x215f:
switchD_005c0b64_caseD_8007215f:
      return (int)"ERROR_DS_DRA_SCHEMA_CONFLICT";
    case 0x2160:
switchD_005c0b64_caseD_80072160:
      return (int)"ERROR_DS_DRA_EARLIER_SCHEMA_CONFLICT";
    case 0x2161:
switchD_005c0b64_caseD_80072161:
      return (int)"ERROR_DS_DRA_OBJ_NC_MISMATCH";
    case 0x2162:
switchD_005c0b64_caseD_80072162:
      return (int)"ERROR_DS_NC_STILL_HAS_DSAS";
    case 0x2163:
switchD_005c0b64_caseD_80072163:
      return (int)"ERROR_DS_GC_REQUIRED";
    case 0x2164:
switchD_005c0b64_caseD_80072164:
      return (int)"ERROR_DS_LOCAL_MEMBER_OF_LOCAL_ONLY";
    case 0x2165:
switchD_005c0b64_caseD_80072165:
      return (int)"ERROR_DS_NO_FPO_IN_UNIVERSAL_GROUPS";
    case 0x2166:
switchD_005c0b64_caseD_80072166:
      return (int)"ERROR_DS_CANT_ADD_TO_GC";
    case 0x2167:
switchD_005c0b64_caseD_80072167:
      return (int)"ERROR_DS_NO_CHECKPOINT_WITH_PDC";
    case 0x2168:
switchD_005c0b64_caseD_80072168:
      return (int)"ERROR_DS_SOURCE_AUDITING_NOT_ENABLED";
    case 0x2169:
switchD_005c0b64_caseD_80072169:
      return (int)"ERROR_DS_CANT_CREATE_IN_NONDOMAIN_NC";
    case 0x216a:
switchD_005c0b64_caseD_8007216a:
      return (int)"ERROR_DS_INVALID_NAME_FOR_SPN";
    case 0x216b:
switchD_005c0b64_caseD_8007216b:
      return (int)"ERROR_DS_FILTER_USES_CONTRUCTED_ATTRS";
    case 0x216c:
switchD_005c0b64_caseD_8007216c:
      return (int)"ERROR_DS_UNICODEPWD_NOT_IN_QUOTES";
    case 0x216d:
switchD_005c0b64_caseD_8007216d:
      return (int)"ERROR_DS_MACHINE_ACCOUNT_QUOTA_EXCEEDED";
    case 0x216e:
switchD_005c0b64_caseD_8007216e:
      return (int)"ERROR_DS_MUST_BE_RUN_ON_DST_DC";
    case 0x216f:
switchD_005c0b64_caseD_8007216f:
      return (int)"ERROR_DS_SRC_DC_MUST_BE_SP4_OR_GREATER";
    case 0x2170:
switchD_005c0b64_caseD_80072170:
      return (int)"ERROR_DS_CANT_TREE_DELETE_CRITICAL_OBJ";
    case 0x2171:
switchD_005c0b64_caseD_80072171:
      return (int)"ERROR_DS_INIT_FAILURE_CONSOLE";
    case 0x2172:
switchD_005c0b64_caseD_80072172:
      return (int)"ERROR_DS_SAM_INIT_FAILURE_CONSOLE";
    case 0x2173:
switchD_005c0b64_caseD_80072173:
      return (int)"ERROR_DS_FOREST_VERSION_TOO_HIGH";
    case 0x2174:
switchD_005c0b64_caseD_80072174:
      return (int)"ERROR_DS_DOMAIN_VERSION_TOO_HIGH";
    case 0x2175:
switchD_005c0b64_caseD_80072175:
      return (int)"ERROR_DS_FOREST_VERSION_TOO_LOW";
    case 0x2176:
switchD_005c0b64_caseD_80072176:
      return (int)"ERROR_DS_DOMAIN_VERSION_TOO_LOW";
    case 0x2177:
switchD_005c0b64_caseD_80072177:
      return (int)"ERROR_DS_INCOMPATIBLE_VERSION";
    case 0x2178:
switchD_005c0b64_caseD_80072178:
      return (int)"ERROR_DS_LOW_DSA_VERSION";
    case 0x2179:
switchD_005c0b64_caseD_80072179:
      return (int)"ERROR_DS_NO_BEHAVIOR_VERSION_IN_MIXEDDOMAIN";
    case 0x217a:
switchD_005c0b64_caseD_8007217a:
      return (int)"ERROR_DS_NOT_SUPPORTED_SORT_ORDER";
    case 0x217b:
switchD_005c0b64_caseD_8007217b:
      return (int)"ERROR_DS_NAME_NOT_UNIQUE";
    case 0x217c:
switchD_005c0b64_caseD_8007217c:
      return (int)"ERROR_DS_MACHINE_ACCOUNT_CREATED_PRENT4";
    case 0x217d:
switchD_005c0b64_caseD_8007217d:
      return (int)"ERROR_DS_OUT_OF_VERSION_STORE";
    case 0x217e:
switchD_005c0b64_caseD_8007217e:
      return (int)"ERROR_DS_INCOMPATIBLE_CONTROLS_USED";
    case 0x217f:
switchD_005c0b64_caseD_8007217f:
      return (int)"ERROR_DS_NO_REF_DOMAIN";
    case 0x2180:
switchD_005c0b64_caseD_80072180:
      return (int)"ERROR_DS_RESERVED_LINK_ID";
    case 0x2181:
switchD_005c0b64_caseD_80072181:
      return (int)"ERROR_DS_LINK_ID_NOT_AVAILABLE";
    case 0x2182:
switchD_005c0b64_caseD_80072182:
      return (int)"ERROR_DS_AG_CANT_HAVE_UNIVERSAL_MEMBER";
    case 0x2183:
switchD_005c0b64_caseD_80072183:
      return (int)"ERROR_DS_MODIFYDN_DISALLOWED_BY_INSTANCE_TYPE";
    case 0x2184:
switchD_005c0b64_caseD_80072184:
      return (int)"ERROR_DS_NO_OBJECT_MOVE_IN_SCHEMA_NC";
    case 0x2185:
switchD_005c0b64_caseD_80072185:
      return (int)"ERROR_DS_MODIFYDN_DISALLOWED_BY_FLAG";
    case 0x2186:
switchD_005c0b64_caseD_80072186:
      return (int)"ERROR_DS_MODIFYDN_WRONG_GRANDPARENT";
    case 0x2187:
switchD_005c0b64_caseD_80072187:
      return (int)"ERROR_DS_NAME_ERROR_TRUST_REFERRAL";
    case 0x2188:
switchD_005c0b64_caseD_80072188:
      return (int)"ERROR_NOT_SUPPORTED_ON_STANDARD_SERVER";
    case 0x2189:
switchD_005c0b64_caseD_80072189:
      return (int)"ERROR_DS_CANT_ACCESS_REMOTE_PART_OF_AD";
    case 0x218a:
switchD_005c0b64_caseD_8007218a:
      return (int)"ERROR_DS_CR_IMPOSSIBLE_TO_VALIDATE_V2";
    case 0x218b:
switchD_005c0b64_caseD_8007218b:
      return (int)"ERROR_DS_THREAD_LIMIT_EXCEEDED";
    case 0x218c:
switchD_005c0b64_caseD_8007218c:
      return (int)"ERROR_DS_NOT_CLOSEST";
    case 0x218d:
switchD_005c0b64_caseD_8007218d:
      return (int)"ERROR_DS_CANT_DERIVE_SPN_WITHOUT_SERVER_REF";
    case 0x218e:
switchD_005c0b64_caseD_8007218e:
      return (int)"ERROR_DS_SINGLE_USER_MODE_FAILED";
    case 0x218f:
switchD_005c0b64_caseD_8007218f:
      return (int)"ERROR_DS_NTDSCRIPT_SYNTAX_ERROR";
    case 0x2190:
switchD_005c0b64_caseD_80072190:
      return (int)"ERROR_DS_NTDSCRIPT_PROCESS_ERROR";
    case 0x2191:
switchD_005c0b64_caseD_80072191:
      return (int)"ERROR_DS_DIFFERENT_REPL_EPOCHS";
    case 0x2192:
switchD_005c0b64_caseD_80072192:
      return (int)"ERROR_DS_DRS_EXTENSIONS_CHANGED";
    case 0x2193:
switchD_005c0b64_caseD_80072193:
      return (int)"ERROR_DS_REPLICA_SET_CHANGE_NOT_ALLOWED_ON_DISABLED_CR";
    case 0x2194:
switchD_005c0b64_caseD_80072194:
      return (int)"ERROR_DS_NO_MSDS_INTID";
    case 0x2195:
switchD_005c0b64_caseD_80072195:
      return (int)"ERROR_DS_DUP_MSDS_INTID";
    case 0x2196:
switchD_005c0b64_caseD_80072196:
      return (int)"ERROR_DS_EXISTS_IN_RDNATTID";
    case 0x2197:
switchD_005c0b64_caseD_80072197:
      return (int)"ERROR_DS_AUTHORIZATION_FAILED";
    case 0x2198:
switchD_005c0b64_caseD_80072198:
      return (int)"ERROR_DS_INVALID_SCRIPT";
    case 0x2199:
switchD_005c0b64_caseD_80072199:
      return (int)"ERROR_DS_REMOTE_CROSSREF_OP_FAILED";
    case 0x219a:
switchD_005c0b64_caseD_8007219a:
      return (int)"ERROR_DS_CROSS_REF_BUSY";
    case 0x219b:
switchD_005c0b64_caseD_8007219b:
      return (int)"ERROR_DS_CANT_DERIVE_SPN_FOR_DELETED_DOMAIN";
    case 0x219c:
switchD_005c0b64_caseD_8007219c:
      return (int)"ERROR_DS_CANT_DEMOTE_WITH_WRITEABLE_NC";
    case 0x219d:
switchD_005c0b64_caseD_8007219d:
      return (int)"ERROR_DS_DUPLICATE_ID_FOUND";
    case 0x219e:
switchD_005c0b64_caseD_8007219e:
      return (int)"ERROR_DS_INSUFFICIENT_ATTR_TO_CREATE_OBJECT";
    case 0x219f:
switchD_005c0b64_caseD_8007219f:
      return (int)"ERROR_DS_GROUP_CONVERSION_ERROR";
    case 0x21a0:
switchD_005c0b64_caseD_800721a0:
      return (int)"ERROR_DS_CANT_MOVE_APP_BASIC_GROUP";
    case 0x21a1:
switchD_005c0b64_caseD_800721a1:
      return (int)"ERROR_DS_CANT_MOVE_APP_QUERY_GROUP";
    case 0x21a2:
switchD_005c0b64_caseD_800721a2:
      return (int)"ERROR_DS_ROLE_NOT_VERIFIED";
    case 0x21a3:
      goto switchD_005c81e1_caseD_21a3;
    case 0x21a4:
switchD_005c81e1_caseD_21a4:
      return (int)"ERROR_DS_DOMAIN_RENAME_IN_PROGRESS";
    case 0x21a5:
switchD_005c81e1_caseD_21a5:
      return (int)"ERROR_DS_EXISTING_AD_CHILD_NC";
    }
  }
  else if (in_stack_00000004 < 0x251d) {
    if (in_stack_00000004 == 0x251c) {
LAB_005c854a:
      return (int)"DNS_ERROR_PACKET_FMT_BASE";
    }
    switch(in_stack_00000004) {
    case 0x2329:
switchD_005c84df_caseD_2329:
      return (int)"DNS_ERROR_RCODE_FORMAT_ERROR";
    case 0x232a:
switchD_005c84df_caseD_232a:
      return (int)"DNS_ERROR_RCODE_SERVER_FAILURE";
    case 0x232b:
switchD_005c84df_caseD_232b:
      return (int)"DNS_ERROR_RCODE_NAME_ERROR";
    case 0x232c:
switchD_005c84df_caseD_232c:
      return (int)"DNS_ERROR_RCODE_NOT_IMPLEMENTED";
    case 0x232d:
switchD_005c84df_caseD_232d:
      return (int)"DNS_ERROR_RCODE_REFUSED";
    case 0x232e:
switchD_005c84df_caseD_232e:
      return (int)"DNS_ERROR_RCODE_YXDOMAIN";
    case 0x232f:
switchD_005c84df_caseD_232f:
      return (int)"DNS_ERROR_RCODE_YXRRSET";
    case 0x2330:
switchD_005c84df_caseD_2330:
      return (int)"DNS_ERROR_RCODE_NXRRSET";
    case 0x2331:
switchD_005c84df_caseD_2331:
      return (int)"DNS_ERROR_RCODE_NOTAUTH";
    case 0x2332:
switchD_005c84df_caseD_2332:
      return (int)"DNS_ERROR_RCODE_NOTZONE";
    case 0x2338:
switchD_005c84df_caseD_2338:
      return (int)"DNS_ERROR_RCODE_BADSIG";
    case 0x2339:
switchD_005c84df_caseD_2339:
      return (int)"DNS_ERROR_RCODE_BADKEY";
    case 0x233a:
switchD_005c84df_caseD_233a:
      return (int)"DNS_ERROR_RCODE_BADTIME";
    }
  }
  else if (in_stack_00000004 < 0x3615) {
    if (in_stack_00000004 == 0x3614) {
switchD_005c0fd9_caseD_80073614:
      return (int)"ERROR_IPSEC_IKE_LOAD_SOFT_SA";
    }
    if (in_stack_00000004 < 0x2752) {
      if (in_stack_00000004 == 0x2751) {
switchD_005c0f73_caseD_80072751:
        return (int)"WSAEHOSTUNREACH";
      }
      switch(in_stack_00000004) {
      case 0x251d:
switchD_005c8591_caseD_251d:
        return (int)"DNS_INFO_NO_RECORDS";
      case 0x251e:
switchD_005c8591_caseD_251e:
        return (int)"DNS_ERROR_BAD_PACKET";
      case 0x251f:
switchD_005c8591_caseD_251f:
        return (int)"DNS_ERROR_NO_PACKET";
      case 0x2520:
switchD_005c8591_caseD_2520:
        return (int)"DNS_ERROR_RCODE";
      case 0x2521:
switchD_005c8591_caseD_2521:
        return (int)"DNS_ERROR_UNSECURE_PACKET";
      case 0x254e:
switchD_005c8591_caseD_254e:
        return (int)"DNS_ERROR_GENERAL_API_BASE";
      case 0x254f:
switchD_005c8591_caseD_254f:
        return (int)"DNS_ERROR_INVALID_TYPE";
      case 0x2550:
switchD_005c8591_caseD_2550:
        return (int)"DNS_ERROR_INVALID_IP_ADDRESS";
      case 0x2551:
switchD_005c8591_caseD_2551:
        return (int)"DNS_ERROR_INVALID_PROPERTY";
      case 0x2552:
switchD_005c8591_caseD_2552:
        return (int)"DNS_ERROR_TRY_AGAIN_LATER";
      case 0x2553:
switchD_005c8591_caseD_2553:
        return (int)"DNS_ERROR_NOT_UNIQUE";
      case 0x2554:
switchD_005c8591_caseD_2554:
        return (int)"DNS_ERROR_NON_RFC_NAME";
      case 0x2555:
switchD_005c8591_caseD_2555:
        return (int)"DNS_STATUS_FQDN";
      case 0x2556:
switchD_005c8591_caseD_2556:
        return (int)"DNS_STATUS_DOTTED_NAME";
      case 0x2557:
switchD_005c8591_caseD_2557:
        return (int)"DNS_STATUS_SINGLE_PART_NAME";
      case 0x2558:
switchD_005c8591_caseD_2558:
        return (int)"DNS_ERROR_INVALID_NAME_CHAR";
      case 0x2559:
switchD_005c8591_caseD_2559:
        return (int)"DNS_ERROR_NUMERIC_NAME";
      case 0x255a:
switchD_005c8591_caseD_255a:
        return (int)"DNS_ERROR_NOT_ALLOWED_ON_ROOT_SERVER";
      case 0x255b:
switchD_005c8591_caseD_255b:
        return (int)"DNS_ERROR_NOT_ALLOWED_UNDER_DELEGATION";
      case 0x255c:
switchD_005c8591_caseD_255c:
        return (int)"DNS_ERROR_CANNOT_FIND_ROOT_HINTS";
      case 0x255d:
switchD_005c8591_caseD_255d:
        return (int)"DNS_ERROR_INCONSISTENT_ROOT_HINTS";
      case 0x2580:
switchD_005c8591_caseD_2580:
        return (int)"DNS_ERROR_ZONE_BASE";
      case 0x2581:
switchD_005c8591_caseD_2581:
        return (int)"DNS_ERROR_ZONE_DOES_NOT_EXIST";
      case 0x2582:
switchD_005c8591_caseD_2582:
        return (int)"DNS_ERROR_NO_ZONE_INFO";
      case 0x2583:
switchD_005c0df2_caseD_80072583:
        return (int)"DNS_ERROR_INVALID_ZONE_OPERATION";
      case 0x2584:
switchD_005c0df2_caseD_80072584:
        return (int)"DNS_ERROR_ZONE_CONFIGURATION_ERROR";
      case 0x2585:
switchD_005c0df2_caseD_80072585:
        return (int)"DNS_ERROR_ZONE_HAS_NO_SOA_RECORD";
      case 0x2586:
switchD_005c0df2_caseD_80072586:
        return (int)"DNS_ERROR_ZONE_HAS_NO_NS_RECORDS";
      case 0x2587:
switchD_005c0df2_caseD_80072587:
        return (int)"DNS_ERROR_ZONE_LOCKED";
      case 0x2588:
switchD_005c0df2_caseD_80072588:
        return (int)"DNS_ERROR_ZONE_CREATION_FAILED";
      case 0x2589:
switchD_005c0df2_caseD_80072589:
        return (int)"DNS_ERROR_ZONE_ALREADY_EXISTS";
      case 0x258a:
switchD_005c0df2_caseD_8007258a:
        return (int)"DNS_ERROR_AUTOZONE_ALREADY_EXISTS";
      case 0x258b:
switchD_005c0df2_caseD_8007258b:
        return (int)"DNS_ERROR_INVALID_ZONE_TYPE";
      case 0x258c:
switchD_005c0df2_caseD_8007258c:
        return (int)"DNS_ERROR_SECONDARY_REQUIRES_MASTER_IP";
      case 0x258d:
switchD_005c0df2_caseD_8007258d:
        return (int)"DNS_ERROR_ZONE_NOT_SECONDARY";
      case 0x258e:
switchD_005c0df2_caseD_8007258e:
        return (int)"DNS_ERROR_NEED_SECONDARY_ADDRESSES";
      case 0x258f:
switchD_005c0df2_caseD_8007258f:
        return (int)"DNS_ERROR_WINS_INIT_FAILED";
      case 0x2590:
switchD_005c0df2_caseD_80072590:
        return (int)"DNS_ERROR_NEED_WINS_SERVERS";
      case 0x2591:
switchD_005c0df2_caseD_80072591:
        return (int)"DNS_ERROR_NBSTAT_INIT_FAILED";
      case 0x2592:
switchD_005c0df2_caseD_80072592:
        return (int)"DNS_ERROR_SOA_DELETE_INVALID";
      case 0x2593:
switchD_005c0df2_caseD_80072593:
        return (int)"DNS_ERROR_FORWARDER_ALREADY_EXISTS";
      case 0x2594:
switchD_005c0df2_caseD_80072594:
        return (int)"DNS_ERROR_ZONE_REQUIRES_MASTER_IP";
      case 0x2595:
switchD_005c0df2_caseD_80072595:
        return (int)"DNS_ERROR_ZONE_IS_SHUTDOWN";
      case 0x25b2:
switchD_005c0df2_caseD_800725b2:
        return (int)"DNS_ERROR_DATAFILE_BASE";
      case 0x25b3:
switchD_005c0df2_caseD_800725b3:
        return (int)"DNS_ERROR_PRIMARY_REQUIRES_DATAFILE";
      case 0x25b4:
switchD_005c0df2_caseD_800725b4:
        return (int)"DNS_ERROR_INVALID_DATAFILE_NAME";
      case 0x25b5:
switchD_005c0df2_caseD_800725b5:
        return (int)"DNS_ERROR_DATAFILE_OPEN_FAILURE";
      case 0x25b6:
switchD_005c0df2_caseD_800725b6:
        return (int)"DNS_ERROR_FILE_WRITEBACK_FAILED";
      case 0x25b7:
switchD_005c0df2_caseD_800725b7:
        return (int)"DNS_ERROR_DATAFILE_PARSING";
      case 0x25e4:
switchD_005c0df2_caseD_800725e4:
        return (int)"DNS_ERROR_DATABASE_BASE";
      case 0x25e5:
switchD_005c0df2_caseD_800725e5:
        return (int)"DNS_ERROR_RECORD_DOES_NOT_EXIST";
      case 0x25e6:
switchD_005c0df2_caseD_800725e6:
        return (int)"DNS_ERROR_RECORD_FORMAT";
      case 0x25e7:
switchD_005c0df2_caseD_800725e7:
        return (int)"DNS_ERROR_NODE_CREATION_FAILED";
      case 0x25e8:
switchD_005c0df2_caseD_800725e8:
        return (int)"DNS_ERROR_UNKNOWN_RECORD_TYPE";
      case 0x25e9:
switchD_005c0df2_caseD_800725e9:
        return (int)"DNS_ERROR_RECORD_TIMED_OUT";
      case 0x25ea:
switchD_005c0df2_caseD_800725ea:
        return (int)"DNS_ERROR_NAME_NOT_IN_ZONE";
      case 0x25eb:
switchD_005c0df2_caseD_800725eb:
        return (int)"DNS_ERROR_CNAME_LOOP";
      case 0x25ec:
switchD_005c0df2_caseD_800725ec:
        return (int)"DNS_ERROR_NODE_IS_CNAME";
      case 0x25ed:
switchD_005c0df2_caseD_800725ed:
        return (int)"DNS_ERROR_CNAME_COLLISION";
      case 0x25ee:
switchD_005c0df2_caseD_800725ee:
        return (int)"DNS_ERROR_RECORD_ONLY_AT_ZONE_ROOT";
      case 0x25ef:
switchD_005c0df2_caseD_800725ef:
        return (int)"DNS_ERROR_RECORD_ALREADY_EXISTS";
      case 0x25f0:
switchD_005c0df2_caseD_800725f0:
        return (int)"DNS_ERROR_SECONDARY_DATA";
      case 0x25f1:
switchD_005c0df2_caseD_800725f1:
        return (int)"DNS_ERROR_NO_CREATE_CACHE_DATA";
      case 0x25f2:
switchD_005c8591_caseD_25f2:
        return (int)"DNS_ERROR_NAME_DOES_NOT_EXIST";
      case 0x25f3:
switchD_005c8591_caseD_25f3:
        return (int)"DNS_WARNING_PTR_CREATE_FAILED";
      case 0x25f4:
switchD_005c8591_caseD_25f4:
        return (int)"DNS_WARNING_DOMAIN_UNDELETED";
      case 0x25f5:
switchD_005c8591_caseD_25f5:
        return (int)"DNS_ERROR_DS_UNAVAILABLE";
      case 0x25f6:
switchD_005c8591_caseD_25f6:
        return (int)"DNS_ERROR_DS_ZONE_ALREADY_EXISTS";
      case 0x25f7:
switchD_005c8591_caseD_25f7:
        return (int)"DNS_ERROR_NO_BOOTFILE_IF_DS_ZONE";
      case 0x2616:
switchD_005c8591_caseD_2616:
        return (int)"DNS_ERROR_OPERATION_BASE";
      case 0x2617:
switchD_005c8591_caseD_2617:
        return (int)"DNS_INFO_AXFR_COMPLETE";
      case 0x2618:
switchD_005c8591_caseD_2618:
        return (int)"DNS_ERROR_AXFR";
      case 0x2619:
switchD_005c8591_caseD_2619:
        return (int)"DNS_INFO_ADDED_LOCAL_WINS";
      case 0x2648:
switchD_005c8591_caseD_2648:
        return (int)"DNS_ERROR_SECURE_BASE";
      case 0x2649:
switchD_005c8591_caseD_2649:
        return (int)"DNS_STATUS_CONTINUE_NEEDED";
      case 0x267a:
switchD_005c8591_caseD_267a:
        return (int)"DNS_ERROR_SETUP_BASE";
      case 0x267b:
switchD_005c8591_caseD_267b:
        return (int)"DNS_ERROR_NO_TCPIP";
      case 0x267c:
switchD_005c8591_caseD_267c:
        return (int)"DNS_ERROR_NO_DNS_SERVERS";
      case 0x26ac:
switchD_005c8591_caseD_26ac:
        return (int)"DNS_ERROR_DP_BASE";
      case 0x26ad:
switchD_005c8591_caseD_26ad:
        return (int)"DNS_ERROR_DP_DOES_NOT_EXIST";
      case 0x26ae:
switchD_005c8591_caseD_26ae:
        return (int)"DNS_ERROR_DP_ALREADY_EXISTS";
      case 0x26af:
switchD_005c8591_caseD_26af:
        return (int)"DNS_ERROR_DP_NOT_ENLISTED";
      case 0x26b0:
switchD_005c8591_caseD_26b0:
        return (int)"DNS_ERROR_DP_ALREADY_ENLISTED";
      case 0x26b1:
switchD_005c8591_caseD_26b1:
        return (int)"DNS_ERROR_DP_NOT_AVAILABLE";
      case 10000:
switchD_005c8591_caseD_2710:
        return (int)"WSABASEERR";
      case 0x2714:
switchD_005c0f44_caseD_80072714:
        return (int)"WSAEINTR";
      case 0x2719:
switchD_005c0f44_caseD_80072719:
        return (int)"WSAEBADF";
      case 0x271d:
switchD_005c0f44_caseD_8007271d:
        return (int)"WSAEACCES";
      case 0x271e:
switchD_005c0f44_caseD_8007271e:
        return (int)"WSAEFAULT";
      case 0x2726:
switchD_005c0f44_caseD_80072726:
        return (int)"WSAEINVAL";
      case 0x2728:
switchD_005c0f44_caseD_80072728:
        return (int)"WSAEMFILE";
      case 0x2733:
switchD_005c0f44_caseD_80072733:
        return (int)"WSAEWOULDBLOCK";
      case 0x2734:
switchD_005c0f44_caseD_80072734:
        return (int)"WSAEINPROGRESS";
      case 0x2735:
switchD_005c0f44_caseD_80072735:
        return (int)"WSAEALREADY";
      case 0x2736:
switchD_005c0f44_caseD_80072736:
        return (int)"WSAENOTSOCK";
      case 0x2737:
switchD_005c0f44_caseD_80072737:
        return (int)"WSAEDESTADDRREQ";
      case 0x2738:
switchD_005c0f44_caseD_80072738:
        return (int)"WSAEMSGSIZE";
      case 0x2739:
switchD_005c0f44_caseD_80072739:
        return (int)"WSAEPROTOTYPE";
      case 0x273a:
switchD_005c0f44_caseD_8007273a:
        return (int)"WSAENOPROTOOPT";
      case 0x273b:
switchD_005c0f44_caseD_8007273b:
        return (int)"WSAEPROTONOSUPPORT";
      case 0x273c:
switchD_005c0f44_caseD_8007273c:
        return (int)"WSAESOCKTNOSUPPORT";
      case 0x273d:
switchD_005c0f44_caseD_8007273d:
        return (int)"WSAEOPNOTSUPP";
      case 0x273e:
switchD_005c0f44_caseD_8007273e:
        return (int)"WSAEPFNOSUPPORT";
      case 0x273f:
switchD_005c0f44_caseD_8007273f:
        return (int)"WSAEAFNOSUPPORT";
      case 0x2740:
switchD_005c8591_caseD_2740:
        return (int)"WSAEADDRINUSE";
      case 0x2741:
switchD_005c0f73_caseD_80072741:
        return (int)"WSAEADDRNOTAVAIL";
      case 0x2742:
switchD_005c0f73_caseD_80072742:
        return (int)"WSAENETDOWN";
      case 0x2743:
switchD_005c0f73_caseD_80072743:
        return (int)"WSAENETUNREACH";
      case 0x2744:
switchD_005c0f73_caseD_80072744:
        return (int)"WSAENETRESET";
      case 0x2745:
switchD_005c0f73_caseD_80072745:
        return (int)"WSAECONNABORTED";
      case 0x2746:
switchD_005c0f73_caseD_80072746:
        return (int)"WSAECONNRESET";
      case 0x2747:
switchD_005c0f73_caseD_80072747:
        return (int)"WSAENOBUFS";
      case 0x2748:
switchD_005c0f73_caseD_80072748:
        return (int)"WSAEISCONN";
      case 0x2749:
switchD_005c0f73_caseD_80072749:
        return (int)"WSAENOTCONN";
      case 0x274a:
switchD_005c0f73_caseD_8007274a:
        return (int)"WSAESHUTDOWN";
      case 0x274b:
switchD_005c0f73_caseD_8007274b:
        return (int)"WSAETOOMANYREFS";
      case 0x274c:
switchD_005c0f73_caseD_8007274c:
        return (int)"WSAETIMEDOUT";
      case 0x274d:
switchD_005c0f73_caseD_8007274d:
        return (int)"WSAECONNREFUSED";
      case 0x274e:
switchD_005c0f73_caseD_8007274e:
        return (int)"WSAELOOP";
      case 0x274f:
switchD_005c0f73_caseD_8007274f:
        return (int)"WSAENAMETOOLONG";
      case 0x2750:
switchD_005c0f73_caseD_80072750:
        return (int)"WSAEHOSTDOWN";
      }
    }
    else if (in_stack_00000004 < 0x32d1) {
      if (in_stack_00000004 == 0x32d0) {
switchD_005c0fbb_caseD_800732d0:
        return (int)"ERROR_IPSEC_TRANSPORT_FILTER_EXISTS";
      }
      if (in_stack_00000004 < 0x2b03) {
        if (in_stack_00000004 == 0x2b02) goto switchD_005c0f97_caseD_80072b02;
        if (in_stack_00000004 < 0x277c) {
          if (in_stack_00000004 == 0x277b) goto switchD_005c0f73_caseD_8007277b;
          switch(in_stack_00000004) {
          case 0x2752:
            goto switchD_005c0f73_caseD_80072752;
          case 0x2753:
            goto switchD_005c0f73_caseD_80072753;
          case 0x2754:
            goto switchD_005c0f73_caseD_80072754;
          case 0x2755:
            goto switchD_005c0f73_caseD_80072755;
          case 0x2756:
            goto switchD_005c0f73_caseD_80072756;
          case 0x2757:
            goto switchD_005c0f73_caseD_80072757;
          case 0x276b:
            goto switchD_005c0f73_caseD_8007276b;
          case 0x276c:
            goto switchD_005c0f73_caseD_8007276c;
          case 0x276d:
            goto switchD_005c0f73_caseD_8007276d;
          case 0x2775:
            goto switchD_005c0f73_caseD_80072775;
          case 0x2776:
            goto switchD_005c0f73_caseD_80072776;
          case 0x2777:
            goto switchD_005c0f73_caseD_80072777;
          case 0x2778:
            goto switchD_005c0f73_caseD_80072778;
          case 0x2779:
            goto switchD_005c0f73_caseD_80072779;
          case 0x277a:
            goto switchD_005c0f73_caseD_8007277a;
          }
        }
        else if (in_stack_00000004 < 0x2afc) {
          if (in_stack_00000004 == 0x2afb) goto switchD_005c0f97_caseD_80072afb;
          if (in_stack_00000004 == 0x277c) goto switchD_005c0f73_caseD_8007277c;
          if (in_stack_00000004 == 0x277d) goto switchD_005c0f73_caseD_8007277d;
          if (in_stack_00000004 == 0x277e) goto switchD_005c0f73_caseD_8007277e;
          if (in_stack_00000004 == 0x277f) goto switchD_005c0f73_caseD_8007277f;
          if (in_stack_00000004 == 0x2780) goto switchD_005c0f73_caseD_80072780;
          if (in_stack_00000004 == 0x2af9) goto LAB_005c8b2d;
          if (in_stack_00000004 == 0x2afa) goto LAB_005c8b23;
        }
        else {
          if (in_stack_00000004 == 0x2afc) goto switchD_005c0f97_caseD_80072afc;
          if (in_stack_00000004 == 0x2afd) goto switchD_005c0f97_caseD_80072afd;
          if (in_stack_00000004 == 0x2afe) goto switchD_005c0f97_caseD_80072afe;
          if (in_stack_00000004 == 0x2aff) goto switchD_005c0f97_caseD_80072aff;
          if (in_stack_00000004 == 0x2b00) goto switchD_005c0f97_caseD_80072b00;
          if (in_stack_00000004 == 0x2b01) goto switchD_005c0f97_caseD_80072b01;
        }
      }
      else if (in_stack_00000004 < 0x32c9) {
        if (in_stack_00000004 == 13000) goto LAB_005c8ccd;
        switch(in_stack_00000004) {
        case 0x2b03:
          goto switchD_005c0f97_caseD_80072b03;
        case 0x2b04:
          goto switchD_005c0f97_caseD_80072b04;
        case 0x2b05:
          goto switchD_005c0f97_caseD_80072b05;
        case 0x2b06:
          goto switchD_005c0f97_caseD_80072b06;
        case 0x2b07:
          goto switchD_005c0f97_caseD_80072b07;
        case 0x2b08:
          goto switchD_005c0f97_caseD_80072b08;
        case 0x2b09:
          goto switchD_005c0f97_caseD_80072b09;
        case 0x2b0a:
          goto switchD_005c0f97_caseD_80072b0a;
        case 0x2b0b:
          goto switchD_005c0f97_caseD_80072b0b;
        case 0x2b0c:
          goto switchD_005c0f97_caseD_80072b0c;
        case 0x2b0d:
          goto switchD_005c0f97_caseD_80072b0d;
        case 0x2b0e:
          goto switchD_005c0f97_caseD_80072b0e;
        case 0x2b0f:
          goto switchD_005c0f97_caseD_80072b0f;
        case 0x2b10:
          goto switchD_005c0f97_caseD_80072b10;
        case 0x2b11:
          goto switchD_005c0f97_caseD_80072b11;
        case 0x2b12:
          goto switchD_005c0f97_caseD_80072b12;
        case 0x2b13:
          goto switchD_005c0f97_caseD_80072b13;
        case 0x2b14:
          goto switchD_005c0f97_caseD_80072b14;
        case 0x2b15:
          goto switchD_005c0f97_caseD_80072b15;
        case 0x2b16:
          goto switchD_005c0f97_caseD_80072b16;
        case 0x2b17:
          goto switchD_005c0f97_caseD_80072b17;
        }
      }
      else {
        if (in_stack_00000004 == 0x32c9) goto switchD_005c0fbb_caseD_800732c9;
        if (in_stack_00000004 == 0x32ca) goto switchD_005c0fbb_caseD_800732ca;
        if (in_stack_00000004 == 0x32cb) goto switchD_005c0fbb_caseD_800732cb;
        if (in_stack_00000004 == 0x32cc) goto switchD_005c0fbb_caseD_800732cc;
        if (in_stack_00000004 == 0x32cd) goto switchD_005c0fbb_caseD_800732cd;
        if (in_stack_00000004 == 0x32ce) goto switchD_005c0fbb_caseD_800732ce;
        if (in_stack_00000004 == 0x32cf) goto switchD_005c0fbb_caseD_800732cf;
      }
    }
    else if (in_stack_00000004 < 0x35e9) {
      if (in_stack_00000004 == 0x35e8) goto LAB_005c8e16;
      switch(in_stack_00000004) {
      case 0x32d1:
        goto switchD_005c0fbb_caseD_800732d1;
      case 0x32d2:
        goto switchD_005c0fbb_caseD_800732d2;
      case 0x32d3:
        goto switchD_005c0fbb_caseD_800732d3;
      case 0x32d4:
        goto switchD_005c0fbb_caseD_800732d4;
      case 0x32d5:
        goto switchD_005c0fbb_caseD_800732d5;
      case 0x32d6:
        goto switchD_005c0fbb_caseD_800732d6;
      case 0x32d7:
        goto switchD_005c0fbb_caseD_800732d7;
      case 0x32d8:
        goto switchD_005c0fbb_caseD_800732d8;
      case 0x32d9:
        goto switchD_005c0fbb_caseD_800732d9;
      case 0x32da:
        goto switchD_005c0fbb_caseD_800732da;
      case 0x32db:
        goto switchD_005c0fbb_caseD_800732db;
      case 0x32dc:
        goto switchD_005c0fbb_caseD_800732dc;
      case 0x32dd:
        goto switchD_005c0fbb_caseD_800732dd;
      case 0x32de:
        goto switchD_005c0fbb_caseD_800732de;
      case 0x32df:
        goto switchD_005c0fbb_caseD_800732df;
      case 0x32e0:
        goto switchD_005c0fbb_caseD_800732e0;
      case 0x32e1:
        goto switchD_005c0fbb_caseD_800732e1;
      }
    }
    else {
      switch(in_stack_00000004) {
      case 0x35e9:
        goto switchD_005c0fd9_caseD_800735e9;
      case 0x35ea:
        goto switchD_005c0fd9_caseD_800735ea;
      case 0x35eb:
        goto switchD_005c0fd9_caseD_800735eb;
      case 0x35ec:
        goto switchD_005c0fd9_caseD_800735ec;
      case 0x35ed:
        goto switchD_005c0fd9_caseD_800735ed;
      case 0x35ee:
        goto switchD_005c0fd9_caseD_800735ee;
      case 0x35ef:
        goto switchD_005c0fd9_caseD_800735ef;
      case 0x35f0:
        goto switchD_005c0fd9_caseD_800735f0;
      case 0x35f1:
        goto switchD_005c0fd9_caseD_800735f1;
      case 0x35f2:
        goto switchD_005c0fd9_caseD_800735f2;
      case 0x35f3:
        goto switchD_005c0fd9_caseD_800735f3;
      case 0x35f4:
        goto switchD_005c0fd9_caseD_800735f4;
      case 0x35f5:
        goto switchD_005c0fd9_caseD_800735f5;
      case 0x35f6:
        goto switchD_005c0fd9_caseD_800735f6;
      case 0x35f7:
        goto switchD_005c0fd9_caseD_800735f7;
      case 0x35f8:
        goto switchD_005c0fd9_caseD_800735f8;
      case 0x35f9:
        goto switchD_005c0fd9_caseD_800735f9;
      case 0x35fa:
        goto switchD_005c0fd9_caseD_800735fa;
      case 0x35fb:
        goto switchD_005c0fd9_caseD_800735fb;
      case 0x35fc:
        goto switchD_005c0fd9_caseD_800735fc;
      case 0x35fe:
        goto switchD_005c0fd9_caseD_800735fe;
      case 0x3600:
        goto switchD_005c0fd9_caseD_80073600;
      case 0x3601:
        goto switchD_005c0fd9_caseD_80073601;
      case 0x3602:
        goto switchD_005c0fd9_caseD_80073602;
      case 0x3603:
        goto switchD_005c0fd9_caseD_80073603;
      case 0x3604:
        goto switchD_005c0fd9_caseD_80073604;
      case 0x3605:
        goto switchD_005c0fd9_caseD_80073605;
      case 0x3606:
        goto switchD_005c0fd9_caseD_80073606;
      case 0x3607:
        goto switchD_005c0fd9_caseD_80073607;
      case 0x3608:
        goto switchD_005c0fd9_caseD_80073608;
      case 0x3609:
        goto switchD_005c0fd9_caseD_80073609;
      case 0x360a:
        goto switchD_005c0fd9_caseD_8007360a;
      case 0x360b:
        goto switchD_005c0fd9_caseD_8007360b;
      case 0x360c:
        goto switchD_005c0fd9_caseD_8007360c;
      case 0x360d:
        goto switchD_005c0fd9_caseD_8007360d;
      case 0x360e:
        goto switchD_005c0fd9_caseD_8007360e;
      case 0x360f:
        goto switchD_005c0fd9_caseD_8007360f;
      case 0x3610:
        goto switchD_005c0fd9_caseD_80073610;
      case 0x3611:
        goto switchD_005c0fd9_caseD_80073611;
      case 0x3612:
        goto switchD_005c0fd9_caseD_80073612;
      case 0x3613:
        goto switchD_005c0fd9_caseD_80073613;
      }
    }
  }
  else if (in_stack_00000004 < 0x36b1) {
    if (in_stack_00000004 == 14000) {
switchD_005c0fd9_caseD_800736b0:
      return (int)"ERROR_SXS_SECTION_NOT_FOUND";
    }
    switch(in_stack_00000004) {
    case 0x3615:
switchD_005c0fd9_caseD_80073615:
      return (int)"ERROR_IPSEC_IKE_SOFT_SA_TORN_DOWN";
    case 0x3616:
switchD_005c0fd9_caseD_80073616:
      return (int)"ERROR_IPSEC_IKE_INVALID_COOKIE";
    case 0x3617:
switchD_005c0fd9_caseD_80073617:
      return (int)"ERROR_IPSEC_IKE_NO_PEER_CERT";
    case 0x3618:
switchD_005c0fd9_caseD_80073618:
      return (int)"ERROR_IPSEC_IKE_PEER_CRL_FAILED";
    case 0x3619:
switchD_005c0fd9_caseD_80073619:
      return (int)"ERROR_IPSEC_IKE_POLICY_CHANGE";
    case 0x361a:
switchD_005c0fd9_caseD_8007361a:
      return (int)"ERROR_IPSEC_IKE_NO_MM_POLICY";
    case 0x361b:
switchD_005c0fd9_caseD_8007361b:
      return (int)"ERROR_IPSEC_IKE_NOTCBPRIV";
    case 0x361c:
switchD_005c0fd9_caseD_8007361c:
      return (int)"ERROR_IPSEC_IKE_SECLOADFAIL";
    case 0x361d:
switchD_005c0fd9_caseD_8007361d:
      return (int)"ERROR_IPSEC_IKE_FAILSSPINIT";
    case 0x361e:
switchD_005c0fd9_caseD_8007361e:
      return (int)"ERROR_IPSEC_IKE_FAILQUERYSSP";
    case 0x361f:
switchD_005c0fd9_caseD_8007361f:
      return (int)"ERROR_IPSEC_IKE_SRVACQFAIL";
    case 0x3620:
switchD_005c0fd9_caseD_80073620:
      return (int)"ERROR_IPSEC_IKE_SRVQUERYCRED";
    case 0x3621:
switchD_005c0fd9_caseD_80073621:
      return (int)"ERROR_IPSEC_IKE_GETSPIFAIL";
    case 0x3622:
switchD_005c0fd9_caseD_80073622:
      return (int)"ERROR_IPSEC_IKE_INVALID_FILTER";
    case 0x3623:
switchD_005c0fd9_caseD_80073623:
      return (int)"ERROR_IPSEC_IKE_OUT_OF_MEMORY";
    case 0x3624:
switchD_005c0fd9_caseD_80073624:
      return (int)"ERROR_IPSEC_IKE_ADD_UPDATE_KEY_FAILED";
    case 0x3625:
switchD_005c0fd9_caseD_80073625:
      return (int)"ERROR_IPSEC_IKE_INVALID_POLICY";
    case 0x3626:
switchD_005c0fd9_caseD_80073626:
      return (int)"ERROR_IPSEC_IKE_UNKNOWN_DOI";
    case 0x3627:
switchD_005c0fd9_caseD_80073627:
      return (int)"ERROR_IPSEC_IKE_INVALID_SITUATION";
    case 0x3628:
switchD_005c0fd9_caseD_80073628:
      return (int)"ERROR_IPSEC_IKE_DH_FAILURE";
    case 0x3629:
switchD_005c0fd9_caseD_80073629:
      return (int)"ERROR_IPSEC_IKE_INVALID_GROUP";
    case 0x362a:
switchD_005c0fd9_caseD_8007362a:
      return (int)"ERROR_IPSEC_IKE_ENCRYPT";
    case 0x362b:
switchD_005c0fd9_caseD_8007362b:
      return (int)"ERROR_IPSEC_IKE_DECRYPT";
    case 0x362c:
switchD_005c0fd9_caseD_8007362c:
      return (int)"ERROR_IPSEC_IKE_POLICY_MATCH";
    case 0x362d:
switchD_005c0fd9_caseD_8007362d:
      return (int)"ERROR_IPSEC_IKE_UNSUPPORTED_ID";
    case 0x362e:
switchD_005c0fd9_caseD_8007362e:
      return (int)"ERROR_IPSEC_IKE_INVALID_HASH";
    case 0x362f:
switchD_005c0fd9_caseD_8007362f:
      return (int)"ERROR_IPSEC_IKE_INVALID_HASH_ALG";
    case 0x3630:
switchD_005c0fd9_caseD_80073630:
      return (int)"ERROR_IPSEC_IKE_INVALID_HASH_SIZE";
    case 0x3631:
switchD_005c0fd9_caseD_80073631:
      return (int)"ERROR_IPSEC_IKE_INVALID_ENCRYPT_ALG";
    case 0x3632:
switchD_005c0fd9_caseD_80073632:
      return (int)"ERROR_IPSEC_IKE_INVALID_AUTH_ALG";
    case 0x3633:
switchD_005c0fd9_caseD_80073633:
      return (int)"ERROR_IPSEC_IKE_INVALID_SIG";
    case 0x3634:
switchD_005c0fd9_caseD_80073634:
      return (int)"ERROR_IPSEC_IKE_LOAD_FAILED";
    case 0x3635:
switchD_005c0fd9_caseD_80073635:
      return (int)"ERROR_IPSEC_IKE_RPC_DELETE";
    case 0x3636:
switchD_005c0fd9_caseD_80073636:
      return (int)"ERROR_IPSEC_IKE_BENIGN_REINIT";
    case 0x3637:
switchD_005c0fd9_caseD_80073637:
      return (int)"ERROR_IPSEC_IKE_INVALID_RESPONDER_LIFETIME_NOTIFY";
    case 0x3639:
switchD_005c0fd9_caseD_80073639:
      return (int)"ERROR_IPSEC_IKE_INVALID_CERT_KEYLEN";
    case 0x363a:
switchD_005c0fd9_caseD_8007363a:
      return (int)"ERROR_IPSEC_IKE_MM_LIMIT";
    case 0x363b:
switchD_005c0fd9_caseD_8007363b:
      return (int)"ERROR_IPSEC_IKE_NEGOTIATION_DISABLED";
    case 0x363c:
switchD_005c0fd9_caseD_8007363c:
      return (int)"ERROR_IPSEC_IKE_NEG_STATUS_END";
    }
  }
  else if (in_stack_00000004 < 0x30201) {
    if (in_stack_00000004 == 0x30200) {
      return (int)"STG_S_CONVERTED";
    }
    switch(in_stack_00000004) {
    case 0x36b1:
switchD_005c0fd9_caseD_800736b1:
      return (int)"ERROR_SXS_CANT_GEN_ACTCTX";
    case 0x36b2:
switchD_005c0fd9_caseD_800736b2:
      return (int)"ERROR_SXS_INVALID_ACTCTXDATA_FORMAT";
    case 0x36b3:
switchD_005c0fd9_caseD_800736b3:
      return (int)"ERROR_SXS_ASSEMBLY_NOT_FOUND";
    case 0x36b4:
switchD_005c0fd9_caseD_800736b4:
      return (int)"ERROR_SXS_MANIFEST_FORMAT_ERROR";
    case 0x36b5:
switchD_005c0fd9_caseD_800736b5:
      return (int)"ERROR_SXS_MANIFEST_PARSE_ERROR";
    case 0x36b6:
switchD_005c0fd9_caseD_800736b6:
      return (int)"ERROR_SXS_ACTIVATION_CONTEXT_DISABLED";
    case 0x36b7:
switchD_005c0fd9_caseD_800736b7:
      return (int)"ERROR_SXS_KEY_NOT_FOUND";
    case 0x36b8:
switchD_005c0fd9_caseD_800736b8:
      return (int)"ERROR_SXS_VERSION_CONFLICT";
    case 0x36b9:
switchD_005c0fd9_caseD_800736b9:
      return (int)"ERROR_SXS_WRONG_SECTION_TYPE";
    case 0x36ba:
switchD_005c0fd9_caseD_800736ba:
      return (int)"ERROR_SXS_THREAD_QUERIES_DISABLED";
    case 0x36bb:
switchD_005c0fd9_caseD_800736bb:
      return (int)"ERROR_SXS_PROCESS_DEFAULT_ALREADY_SET";
    case 0x36bc:
switchD_005c0fd9_caseD_800736bc:
      return (int)"ERROR_SXS_UNKNOWN_ENCODING_GROUP";
    case 0x36bd:
switchD_005c0fd9_caseD_800736bd:
      return (int)"ERROR_SXS_UNKNOWN_ENCODING";
    case 0x36be:
switchD_005c0fd9_caseD_800736be:
      return (int)"ERROR_SXS_INVALID_XML_NAMESPACE_URI";
    case 0x36bf:
switchD_005c0fd9_caseD_800736bf:
      return (int)"ERROR_SXS_ROOT_MANIFEST_DEPENDENCY_NOT_INSTALLED";
    case 0x36c0:
switchD_005c0fd9_caseD_800736c0:
      return (int)"ERROR_SXS_LEAF_MANIFEST_DEPENDENCY_NOT_INSTALLED";
    case 0x36c1:
switchD_005c0fd9_caseD_800736c1:
      return (int)"ERROR_SXS_INVALID_ASSEMBLY_IDENTITY_ATTRIBUTE";
    case 0x36c2:
switchD_005c0fd9_caseD_800736c2:
      return (int)"ERROR_SXS_MANIFEST_MISSING_REQUIRED_DEFAULT_NAMESPACE";
    case 0x36c3:
switchD_005c0fd9_caseD_800736c3:
      return (int)"ERROR_SXS_MANIFEST_INVALID_REQUIRED_DEFAULT_NAMESPACE";
    case 0x36c4:
switchD_005c0fd9_caseD_800736c4:
      return (int)"ERROR_SXS_PRIVATE_MANIFEST_CROSS_PATH_WITH_REPARSE_POINT";
    case 0x36c5:
switchD_005c0fd9_caseD_800736c5:
      return (int)"ERROR_SXS_DUPLICATE_DLL_NAME";
    case 0x36c6:
switchD_005c0fd9_caseD_800736c6:
      return (int)"ERROR_SXS_DUPLICATE_WINDOWCLASS_NAME";
    case 0x36c7:
      goto switchD_005c91b2_caseD_36c7;
    case 0x36c8:
      goto switchD_005c0ff9_caseD_800736c8;
    case 0x36c9:
      goto switchD_005c0ff9_caseD_800736c9;
    case 0x36ca:
      goto switchD_005c0ff9_caseD_800736ca;
    case 0x36cb:
      goto switchD_005c0ff9_caseD_800736cb;
    case 0x36cc:
      goto switchD_005c0ff9_caseD_800736cc;
    case 0x36cd:
      goto switchD_005c0ff9_caseD_800736cd;
    case 0x36ce:
      goto switchD_005c0ff9_caseD_800736ce;
    case 0x36cf:
      goto switchD_005c0ff9_caseD_800736cf;
    case 0x36d0:
      goto switchD_005c0ff9_caseD_800736d0;
    case 0x36d1:
      goto switchD_005c0ff9_caseD_800736d1;
    case 0x36d2:
      goto switchD_005c0ff9_caseD_800736d2;
    case 0x36d3:
      goto switchD_005c0ff9_caseD_800736d3;
    case 0x36d4:
      goto switchD_005c0ff9_caseD_800736d4;
    case 0x36d5:
      goto switchD_005c0ff9_caseD_800736d5;
    case 0x36d6:
      goto switchD_005c0ff9_caseD_800736d6;
    case 0x36d7:
      goto switchD_005c0ff9_caseD_800736d7;
    case 0x36d8:
      goto switchD_005c0ff9_caseD_800736d8;
    case 0x36d9:
      goto switchD_005c0ff9_caseD_800736d9;
    case 0x36da:
      goto switchD_005c0ff9_caseD_800736da;
    case 0x36db:
      goto switchD_005c0ff9_caseD_800736db;
    case 0x36dc:
      goto switchD_005c0ff9_caseD_800736dc;
    case 0x36dd:
      goto switchD_005c0ff9_caseD_800736dd;
    case 0x36de:
      goto switchD_005c0ff9_caseD_800736de;
    case 0x36df:
      goto switchD_005c0ff9_caseD_800736df;
    case 0x36e0:
      goto switchD_005c0ff9_caseD_800736e0;
    case 0x36e1:
      goto switchD_005c0ff9_caseD_800736e1;
    case 0x36e2:
      goto switchD_005c0ff9_caseD_800736e2;
    case 0x36e3:
      goto switchD_005c0ff9_caseD_800736e3;
    case 0x36e4:
      goto switchD_005c0ff9_caseD_800736e4;
    case 0x36e5:
      goto switchD_005c0ff9_caseD_800736e5;
    case 0x36e6:
      goto switchD_005c0ff9_caseD_800736e6;
    case 0x36e7:
      goto switchD_005c0ff9_caseD_800736e7;
    case 0x36e8:
      goto switchD_005c0ff9_caseD_800736e8;
    case 0x36e9:
      goto switchD_005c0ff9_caseD_800736e9;
    case 0x36ea:
      goto switchD_005c0ff9_caseD_800736ea;
    case 0x36eb:
      goto switchD_005c0ff9_caseD_800736eb;
    case 0x36ec:
      goto switchD_005c0ff9_caseD_800736ec;
    case 0x36ed:
      goto switchD_005c0ff9_caseD_800736ed;
    case 0x36ee:
      goto switchD_005c0ff9_caseD_800736ee;
    case 0x36ef:
      goto switchD_005c0ff9_caseD_800736ef;
    case 0x36f0:
      goto switchD_005c0ff9_caseD_800736f0;
    case 0x36f1:
      goto switchD_005c0ff9_caseD_800736f1;
    case 0x36f2:
      goto switchD_005c0ff9_caseD_800736f2;
    case 0x36f3:
      goto switchD_005c0ff9_caseD_800736f3;
    case 0x36f4:
      goto switchD_005c0ff9_caseD_800736f4;
    case 0x36f5:
      goto switchD_005c0ff9_caseD_800736f5;
    case 0x36f6:
      goto switchD_005c0ff9_caseD_800736f6;
    case 0x36f7:
      goto switchD_005c0ff9_caseD_800736f7;
    case 0x36f8:
      goto switchD_005c0ff9_caseD_800736f8;
    case 0x36f9:
      goto switchD_005c0ff9_caseD_800736f9;
    case 0x36fa:
      goto switchD_005c0ff9_caseD_800736fa;
    case 0x36fb:
      goto switchD_005c0ff9_caseD_800736fb;
    case 0x36fc:
      goto switchD_005c0ff9_caseD_800736fc;
    case 0x36fd:
      goto switchD_005c0ff9_caseD_800736fd;
    case 0x36fe:
      goto switchD_005c0ff9_caseD_800736fe;
    case 0x36ff:
      goto switchD_005c0ff9_caseD_800736ff;
    case 0x3700:
      goto switchD_005c0ff9_caseD_80073700;
    }
  }
  else if (in_stack_00000004 < 0x4025b) {
    if (in_stack_00000004 == 0x4025a) {
      return (int)"VFW_S_RPZA";
    }
    if (in_stack_00000004 < 0x40182) {
      if (in_stack_00000004 == 0x40181) {
        return (int)"OLEOBJ_S_CANNOT_DOVERB_NOW";
      }
      if (in_stack_00000004 < 0x40111) {
        if (in_stack_00000004 == 0x40110) {
          return (int)"CLASSFACTORY_S_FIRST";
        }
        if (in_stack_00000004 < 0x40002) {
          if (in_stack_00000004 == 0x40001) {
            return (int)"OLE_S_STATIC & MS_S_PENDING";
          }
          if (in_stack_00000004 == 0x30201) {
            return (int)"STG_S_BLOCK";
          }
          if (in_stack_00000004 == 0x30202) {
            return (int)"STG_S_RETRYNOW";
          }
          if (in_stack_00000004 == 0x30203) {
            return (int)"STG_S_MONITORING";
          }
          if (in_stack_00000004 == 0x30204) {
            return (int)"STG_S_MULTIPLEOPENS";
          }
          if (in_stack_00000004 == 0x30205) {
            return (int)"STG_S_CONSOLIDATIONFAILED";
          }
          if (in_stack_00000004 == 0x30206) {
            return (int)"STG_S_CANNOTCONSOLIDATE";
          }
          if (in_stack_00000004 == 0x40000) {
            return (int)"OLE_S_FIRST";
          }
        }
        else {
          if (in_stack_00000004 == 0x40002) {
            return (int)"OLE_S_MAC_CLIPFORMAT & MS_S_NOUPDATE";
          }
          if (in_stack_00000004 == 0x400ff) {
            return (int)"OLE_S_LAST";
          }
          if (in_stack_00000004 == 0x40100) {
            return (int)"DRAGDROP_S_FIRST";
          }
          if (in_stack_00000004 == 0x40101) {
            return (int)"DRAGDROP_S_CANCEL";
          }
          if (in_stack_00000004 == 0x40102) {
            return (int)"DRAGDROP_S_USEDEFAULTCURSORS";
          }
          if (in_stack_00000004 == 0x40103) {
            return (int)"VFW_S_NO_MORE_ITEMS";
          }
          if (in_stack_00000004 == 0x4010f) {
            return (int)"DRAGDROP_S_LAST";
          }
        }
      }
      else if (in_stack_00000004 < 0x40151) {
        if (in_stack_00000004 == 0x40150) {
          return (int)"REGDB_S_FIRST";
        }
        if (in_stack_00000004 == 0x4011f) {
          return (int)"CLASSFACTORY_S_LAST";
        }
        if (in_stack_00000004 == 0x40120) {
          return (int)"MARSHAL_S_FIRST";
        }
        if (in_stack_00000004 == 0x4012f) {
          return (int)"MARSHAL_S_LAST";
        }
        if (in_stack_00000004 == 0x40130) {
          return (int)"DATA_S_FIRST";
        }
        if (in_stack_00000004 == 0x4013f) {
          return (int)"DATA_S_LAST";
        }
        if (in_stack_00000004 == 0x40140) {
          return (int)"VIEW_S_FIRST";
        }
        if (in_stack_00000004 == 0x4014f) {
          return (int)"VIEW_S_LAST";
        }
      }
      else {
        if (in_stack_00000004 == 0x4015f) {
          return (int)"REGDB_S_LAST";
        }
        if (in_stack_00000004 == 0x40170) {
          return (int)"CACHE_S_FIRST";
        }
        if (in_stack_00000004 == 0x40171) {
          return (int)"CACHE_S_SAMECACHE";
        }
        if (in_stack_00000004 == 0x40172) {
          return (int)"CACHE_S_SOMECACHES_NOTUPDATED";
        }
        if (in_stack_00000004 == 0x4017f) {
          return (int)"CACHE_S_LAST";
        }
        if (in_stack_00000004 == 0x40180) {
          return (int)"OLEOBJ_S_FIRST";
        }
      }
    }
    else if (in_stack_00000004 < 0x401e5) {
      if (in_stack_00000004 == 0x401e4) {
        return (int)"MK_S_ME";
      }
      if (in_stack_00000004 < 0x401c0) {
        if (in_stack_00000004 == 0x401bf) {
          return (int)"ENUM_S_LAST";
        }
        if (in_stack_00000004 == 0x40182) {
          return (int)"OLEOBJ_S_INVALIDHWND";
        }
        if (in_stack_00000004 == 0x4018f) {
          return (int)"OLEOBJ_S_LAST";
        }
        if (in_stack_00000004 == 0x40190) {
          return (int)"CLIENTSITE_S_FIRST";
        }
        if (in_stack_00000004 == 0x4019f) {
          return (int)"CLIENTSITE_S_LAST";
        }
        if (in_stack_00000004 == 0x401a0) {
          return (int)"INPLACE_S_FIRST";
        }
        if (in_stack_00000004 == 0x401af) {
          return (int)"INPLACE_S_LAST";
        }
        if (in_stack_00000004 == 0x401b0) {
          return (int)"ENUM_S_FIRST";
        }
      }
      else {
        if (in_stack_00000004 == 0x401c0) {
          return (int)"CONVERT10_S_FIRST";
        }
        if (in_stack_00000004 == 0x401cf) {
          return (int)"CONVERT10_S_LAST";
        }
        if (in_stack_00000004 == 0x401d0) {
          return (int)"CLIPBRD_S_FIRST";
        }
        if (in_stack_00000004 == 0x401df) {
          return (int)"CLIPBRD_S_LAST";
        }
        if (in_stack_00000004 == 0x401e0) {
          return (int)"MK_S_FIRST";
        }
        if (in_stack_00000004 == 0x401e2) {
          return (int)"MK_S_REDUCED_TO_SELF";
        }
      }
    }
    else if (in_stack_00000004 < 0x40243) {
      if (in_stack_00000004 == 0x40242) {
        return (int)"VFW_S_PARTIAL_RENDER";
      }
      if (in_stack_00000004 == 0x401e5) {
        return (int)"MK_S_HIM";
      }
      if (in_stack_00000004 == 0x401e6) {
        return (int)"MK_S_US";
      }
      if (in_stack_00000004 == 0x401e7) {
        return (int)"MK_S_MONIKERALREADYREGISTERED";
      }
      if (in_stack_00000004 == 0x401ef) {
        return (int)"MK_S_LAST";
      }
      if (in_stack_00000004 == 0x40202) {
        return (int)"EVENT_S_NOSUBSCRIBERS";
      }
      if (in_stack_00000004 == 0x4022d) {
        return (int)"VFW_S_DUPLICATE_NAME";
      }
      if (in_stack_00000004 == 0x40237) {
        return (int)"VFW_S_STATE_INTERMEDIATE";
      }
    }
    else {
      if (in_stack_00000004 == 0x40245) {
        return (int)"VFW_S_SOME_DATA_IGNORED";
      }
      if (in_stack_00000004 == 0x40246) {
        return (int)"VFW_S_CONNECTIONS_DEFERRED";
      }
      if (in_stack_00000004 == 0x40250) {
        return (int)"VFW_S_RESOURCE_NOT_NEEDED";
      }
      if (in_stack_00000004 == 0x40254) {
        return (int)"VFW_S_MEDIA_TYPE_IGNORED";
      }
      if (in_stack_00000004 == 0x40257) {
        return (int)"VFW_S_VIDEO_NOT_RENDERED";
      }
      if (in_stack_00000004 == 0x40258) {
        return (int)"VFW_S_AUDIO_NOT_RENDERED";
      }
    }
  }
  else if (in_stack_00000004 < 0x4e001) {
    if (in_stack_00000004 == 0x4e000) {
      return (int)"CONTEXT_S_FIRST";
    }
    if (in_stack_00000004 < 0x41307) {
      if (in_stack_00000004 == 0x41306) {
        return (int)"SCHED_S_TASK_TERMINATED";
      }
      if (in_stack_00000004 < 0x4028d) {
        if (in_stack_00000004 == 0x4028c) {
          return (int)"VFW_S_DVD_CHANNEL_CONTENTS_NOT_AVAILABLE";
        }
        if (in_stack_00000004 == 0x40260) {
          return (int)"VFW_S_ESTIMATED";
        }
        if (in_stack_00000004 == 0x40263) {
          return (int)"VFW_S_RESERVED";
        }
        if (in_stack_00000004 == 0x40267) {
          return (int)"VFW_S_STREAM_OFF";
        }
        if (in_stack_00000004 == 0x40268) {
          return (int)"VFW_S_CANT_CUE";
        }
        if (in_stack_00000004 == 0x40270) {
          return (int)"VFW_S_NO_STOP_TIME";
        }
        if (in_stack_00000004 == 0x4027e) {
          return (int)"VFW_S_NOPREVIEWPIN";
        }
        if (in_stack_00000004 == 0x40280) {
          return (int)"VFW_S_DVD_NON_ONE_SEQUENTIAL";
        }
      }
      else {
        if (in_stack_00000004 == 0x4028d) {
          return (int)"VFW_S_DVD_NOT_ACCURATE";
        }
        if (in_stack_00000004 == 0x41300) {
          return (int)"SCHED_S_TASK_READY";
        }
        if (in_stack_00000004 == 0x41301) {
          return (int)"SCHED_S_TASK_RUNNING";
        }
        if (in_stack_00000004 == 0x41302) {
          return (int)"SCHED_S_TASK_DISABLED";
        }
        if (in_stack_00000004 == 0x41303) {
          return (int)"SCHED_S_TASK_HAS_NOT_RUN";
        }
        if (in_stack_00000004 == 0x41304) {
          return (int)"SCHED_S_TASK_NO_MORE_RUNS";
        }
        if (in_stack_00000004 == 0x41305) {
          return (int)"SCHED_S_TASK_NOT_SCHEDULED";
        }
      }
    }
    else if (in_stack_00000004 < 0x4d006) {
      if (in_stack_00000004 == 0x4d005) {
        return (int)"XACT_S_MADECHANGESCONTENT";
      }
      if (in_stack_00000004 == 0x41307) {
        return (int)"SCHED_S_TASK_NO_VALID_TRIGGERS";
      }
      if (in_stack_00000004 == 0x41308) {
        return (int)"SCHED_S_EVENT_TRIGGER";
      }
      if (in_stack_00000004 == 0x4d000) {
        return (int)"XACT_S_FIRST";
      }
      if (in_stack_00000004 == 0x4d001) {
        return (int)"XACT_S_DEFECT";
      }
      if (in_stack_00000004 == 0x4d002) {
        return (int)"XACT_S_READONLY";
      }
      if (in_stack_00000004 == 0x4d003) {
        return (int)"XACT_S_SOMENORETAIN";
      }
      if (in_stack_00000004 == 0x4d004) {
        return (int)"XACT_S_OKINFORM";
      }
    }
    else {
      if (in_stack_00000004 == 0x4d006) {
        return (int)"XACT_S_MADECHANGESINFORM";
      }
      if (in_stack_00000004 == 0x4d007) {
        return (int)"XACT_S_ALLNORETAIN";
      }
      if (in_stack_00000004 == 0x4d008) {
        return (int)"XACT_S_ABORTING";
      }
      if (in_stack_00000004 == 0x4d009) {
        return (int)"XACT_S_SINGLEPHASE";
      }
      if (in_stack_00000004 == 0x4d00a) {
        return (int)"XACT_S_LOCALLY_OK";
      }
      if (in_stack_00000004 == 0x4d010) {
        return (int)"XACT_S_LAST";
      }
    }
  }
  else if (in_stack_00000004 < 0x150011) {
    if (in_stack_00000004 == 0x150010) {
      return (int)"DV_PENDING";
    }
    if (in_stack_00000004 < 0x90318) {
      if (in_stack_00000004 == 0x90317) {
        return (int)"SEC_I_CONTEXT_EXPIRED";
      }
      if (in_stack_00000004 == 0x4e02f) {
        return (int)"CONTEXT_S_LAST";
      }
      if (in_stack_00000004 == 0x80012) {
        return (int)"CO_S_NOTALLINTERFACES";
      }
      if (in_stack_00000004 == 0x80013) {
        return (int)"CO_S_MACHINENAMENOTFOUND";
      }
      if (in_stack_00000004 == 0x90312) {
        return (int)"SEC_I_CONTINUE_NEEDED";
      }
      if (in_stack_00000004 == 0x90313) {
        return (int)"SEC_I_COMPLETE_NEEDED";
      }
      if (in_stack_00000004 == 0x90314) {
        return (int)"SEC_I_COMPLETE_AND_CONTINUE";
      }
      if (in_stack_00000004 == 0x90315) {
        return (int)"SEC_I_LOCAL_LOGON";
      }
    }
    else {
      if (in_stack_00000004 == 0x90320) {
        return (int)"SEC_I_INCOMPLETE_CREDENTIALS";
      }
      if (in_stack_00000004 == 0x90321) {
        return (int)"SEC_I_RENEGOTIATE";
      }
      if (in_stack_00000004 == 0x90323) {
        return (int)"SEC_I_NO_LSA_CONTEXT";
      }
      if (in_stack_00000004 == 0x91012) {
        return (int)"CRYPT_I_NEW_PROTECTION_REQUIRED";
      }
      if (in_stack_00000004 == 0x150005) {
        return (int)"DV_FULLDUPLEX";
      }
      if (in_stack_00000004 == 0x15000a) {
        return (int)"DV_HALFDUPLEX";
      }
    }
  }
  else if (in_stack_00000004 < 0x8781211) {
    if (in_stack_00000004 == 0x8781210) {
      return (int)"DMUS_S_STRING_TRUNCATED";
    }
    if (in_stack_00000004 == 0x876086f) {
      return (int)"D3DOK_NOAUTOGEN";
    }
    if (in_stack_00000004 == 0x878000a) {
      return (int)"DS_NO_VIRTUALIZATION";
    }
    if (in_stack_00000004 == 0x8781091) {
      return (int)"DMUS_S_PARTIALLOAD";
    }
    if (in_stack_00000004 == 0x8781092) {
      return (int)"DMUS_S_PARTIALDOWNLOAD";
    }
    if (in_stack_00000004 == 0x8781200) {
      return (int)"DMUS_S_REQUEUE";
    }
    if (in_stack_00000004 == 0x8781201) {
      return (int)"DMUS_S_FREE";
    }
    if (in_stack_00000004 == 0x8781202) {
      return (int)"DMUS_S_END";
    }
  }
  else {
    if (in_stack_00000004 == 0x8781211) {
      return (int)"DMUS_S_LAST_TOOL";
    }
    if (in_stack_00000004 == 0x8781212) {
      return (int)"DMUS_S_OVER_CHORD";
    }
    if (in_stack_00000004 == 0x8781213) {
      return (int)"DMUS_S_UP_OCTAVE";
    }
    if (in_stack_00000004 == 0x8781214) {
      return (int)"DMUS_S_DOWN_OCTAVE";
    }
    if (in_stack_00000004 == 0x8781215) {
      return (int)"DMUS_S_NOBUFFERCONTROL";
    }
    if (in_stack_00000004 == 0x8781216) {
      return (int)"DMUS_S_GARBAGE_COLLECTED";
    }
  }
  return (int)"Unknown";
}
